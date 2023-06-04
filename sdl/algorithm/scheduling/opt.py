from sdl.algorithm.scheduling.io import SchedulingDecisions
from sdl.lab import Job, SDLLab
from pulp import *
from typing import Any, List, Optional


def solve(
        lab: SDLLab,
        jobs: List[Job],
        msg: bool = False,
        limit: Optional[int] = None,
        time_limit: Optional[int] = None
) -> SchedulingDecisions:  # dict[str, Any]:
    """
    The ILP provided in this file is from the paper, "Mathematical models for job-shop scheduling
    problems with routing and process plan flexibility" by Özgüven et al. in Applied Mathematical
    Modeling (2010).

    NOTE:
    The `limit` value is the most sensitive part about the solver. Results change drastically
    depending on the value of `limit`. If it is too big, the solver may think the problem
    is infeasible and give us "broken" schedules.
    """
    if limit is None:
        limit = 1_000_000  # int(1e18)

    # Initialize the ILP.
    model = LpProblem('SDL-Scheduling', LpMinimize)

    J = [j for j in range(len(jobs))]
    JOM = [
        (j, o, m)
        for j, job in enumerate(jobs)
        for o, op in enumerate(job.ops)
        for m in lab.machines_that_can_do(op)
    ]
    JOJOM = [
        (j1, o1, j2, o2, m)
        for j1, job1 in enumerate(jobs)
        for o1, op1 in enumerate(job1.ops)
        for j2, job2 in enumerate(jobs)
        for o2, op2 in enumerate(job2.ops)
        for m in set(lab.machines_that_can_do(op1)).intersection(set(lab.machines_that_can_do(op2)))
        if j1 != j2
    ]

    # Initialize the decision variables.
    x = LpVariable.dicts('Machine-operation assignments', JOM, cat=LpBinary)
    s = LpVariable.dicts('Starting times', JOM, cat=LpContinuous, lowBound=0, upBound=limit)
    c = LpVariable.dicts('Completion times', JOM, cat=LpContinuous, lowBound=0, upBound=limit)
    y = LpVariable.dicts('Operation precedence', JOJOM, cat=LpBinary)
    t = LpVariable.dicts('Total completion time', J, cat=LpContinuous, lowBound=0, upBound=limit)
    makespan = LpVariable('Makespan', lowBound=0, upBound=None, cat=LpContinuous)

    # Initialize objective function.
    model += makespan

    # Initialize the constraints.
    # Constraint (1): Ensure Operation [jo] is assigned to only one machine.
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            model += lpSum(x[j, o, m] for m in lab.machines_that_can_do(op)) == 1

    # Constraint (2): Guarantees that the start time + completion time of (j, o, m) decisions
    #                 is within bounds.
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            for m in lab.machines_that_can_do(op):
                model += s[j, o, m] + c[j, o, m] <= x[j, o, m] * limit

    # Constraint (3): Ensures completion time is after start time after processing time.
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            proc = lab.proc_time(op.opcode)
            for m in lab.machines_that_can_do(op):
                model += c[j, o, m] >= s[j, o, m] + proc - (1 - x[j, o, m]) * limit

    # Constraints (4) and (5): Ensures that there are no overlapping operation_pool run on
    #                          the same machine.
    for j1, job1 in enumerate(jobs):
        for j2, job2 in enumerate(jobs):
            if j1 == j2:
                continue
            for o1, op1 in enumerate(job1.ops):
                for o2, op2 in enumerate(job2.ops):
                    m1_set = set(lab.machines_that_can_do(op1))
                    m2_set = set(lab.machines_that_can_do(op2))
                    for m in m1_set.intersection(m2_set):
                        model += s[j1, o1, m] >= c[j2, o2, m] - y[j1, o1, j2, o2, m] * limit
                        model += s[j2, o2, m] >= c[j1, o1, m] - (1 - y[j1, o1, j2, o2, m]) * limit

    # Constraint (6): Ensures that a job's operation ends before the next operation starts.
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            if o > 0:
                m_set1 = lab.machines_that_can_do(op)
                m_set2 = lab.machines_that_can_do(job.ops[o - 1])
                model += lpSum(s[j, o, m] for m in m_set1) >= lpSum(c[j, o - 1, m] for m in m_set2)

    # Constraint (7): Guarantees that total time is at least as large as the last operation's
    #                 completion time, for each job.
    for j, job in enumerate(jobs):
        last_o, last_op = len(job.ops) - 1, job.ops[-1]
        model += t[j] >= lpSum(c[j, last_o, m] for m in lab.machines_that_can_do(last_op))

    # Constraint (8): Ensures makespan is larger than all total completion times.
    for j in range(len(jobs)):
        model += makespan >= t[j]

    # Solve the problem, convert the decision variables into dicts, and return.
    solver = PULP_CBC_CMD(msg=msg, timeLimit=time_limit)
    model.solve(solver)

    x = {key: x[key].value() for key in x}
    s = {key: s[key].value() for key in s}
    c = {key: c[key].value() for key in c}
    y = {key: y[key].value() for key in y}
    t = {key: t[key].value() for key in t}

    print("x:", x)
    print("s:", s)
    print("c:", c)
    print("y:", y)
    print("t:", t)
    # return dict(makespan=SP.value(), x=x, s=s, c=c, y=y, t=t)
    return SchedulingDecisions(
        makespan=makespan.value(),
        machine_operations=x,
        starting_times=s,
        completion_times=c,
        operation_prec=y,
        total_time=t
    )
