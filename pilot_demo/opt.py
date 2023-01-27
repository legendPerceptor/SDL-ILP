from pilot_demo.lab import Job, SDLLab
from pulp import *
from typing import List

INF = int(1e20)
# INF = 1

def schedule(lab: SDLLab, jobs: List[Job], msg: bool=False):
    # Initialize the problem itself.
    model = LpProblem('SDL-Scheduling', LpMinimize)

    # Initialize the set of indices to be used by the decision variables below.
    num_slots = sum(len(j) for j in jobs)
    jo = [(j, o) for j in range(len(jobs)) for o in range(len(jobs[j].ops))]
    ms = [(m, s) for m in range(len(lab.machines)) for s in range(num_slots)]
    jom = [(j, o, m)
        for j in range(len(jobs))
        for o in range(len(jobs[j].ops))
        for m in range(len(lab.machines))
    ]
    joms = [(j, o, m, s)
        for j in range(len(jobs))
        for o in range(len(jobs[j].ops))
        for m in range(len(lab.machines))
        for s in range(num_slots)
    ]

    # Declare/initialize the decision variables.
    makespan = LpVariable('Makespan (SP)', lowBound=0, upBound=None, cat=LpInteger)
    b = LpVariable.dicts('Beginning Operation Times', jo, lowBound=0, upBound=None, cat=LpInteger)
    t = LpVariable.dicts('Startup Times', ms, lowBound=0, upBound=None, cat=LpInteger)
    x = LpVariable.dicts('Operation-Machine Slot Assignment', joms, cat=LpBinary)
    y = LpVariable.dicts('Operation-Machine Assignment', jom, cat=LpBinary)

    # Objective function, i.e., to minimize overall makespan.
    model += makespan

    # Constraint (a): Makespan must be larger than the longest completion time.
    for (j, job) in enumerate(jobs):
        # last_o = job.ops[-1].opcode
        last_o = len(job.ops) - 1
        op = job.ops[last_o]
        model += b[j, last_o] + lab.proc_time(op.opcode) <= makespan

    # Constraint (b): Ensure operations for each job happen in-order.
    for (j, job) in enumerate(jobs):
        for o, op in enumerate(job.ops[:-1]):
            model += b[j, o] + lab.proc_time(op.opcode) <= b[j, o + 1]

    # Constraint (c): Ensure no overlapping operations run on any one machine in a slot.
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            p = lab.proc_time(op.opcode)
            for m in range(len(lab.machines)):
                for s in range(num_slots - 1):
                    model += t[m, s] + x[j, o, m, s] * p <= t[m, s + 1]

    # Constraints (D) and (E): ...
    for m in range(len(lab.machines)):
        for s in range(num_slots):
            for j, job in enumerate(jobs):
                for o in range(len(job.ops)):
                    L = int(1e20) # 1234567890
                    model += t[m, s] <= b[j, o] + L * (1 - x[j, o, m, s])
                    model += b[j, o] <= t[m, s] + L * (1 - x[j, o, m, s])

    '''
    # Constraint (d): Startup time must respect beginning times of operations.
    for m in range(len(lab.machines)):
        for s in range(num_slots):
            for j, job in enumerate(jobs):
                for o in range(len(job.ops)):
                    model += t[m, s] <= b[j, o] + INF * (1 - x[j, o, m, s])

    # Constraint (e): ...
    for m in range(len(lab.machines)):
        for s in range(num_slots):
            for j, job in enumerate(jobs):
                for o in range(len(job.ops)):
                    model += b[j, o] <= t[m, s] + INF * (1 - x[j, o, m, s])
    '''

    # Constraint: Each job operation has to be performed exactly once.
    # for j, job in enumerate(jobs):
    #     for o in range(len(job.ops)):
    #         model += lpSum(x[j, o, m, s] for m in range(len(lab.machines)) for s in range(num_slots)) == 1
    #
    # for m in range(len(lab.machines)):
    #     for s in range(num_slots):
    #         model += lpSum(x[j, o, m, s] for j, job in enumerate(jobs) for o in range(len(job.ops))) <= 1

    # Constraint (f): ...
    # for j, job in enumerate(jobs):
    #     for o in range(len(job.ops)):
    #         for m in range(len(lab.machines)):
    #             model += lpSum(x[j, o, m, s] for s in range(num_slots)) <= 1


    # Constraint (g): ...
    # for m in range(len(lab.machines)):
    #     for s in range(num_slots):
    #         model += lpSum(x[j, o, m, s] for j, job in enumerate(jobs) for o in range(len(job.ops))) <= 1

    # Constraint (h): ...
    for j, job in enumerate(jobs):
        for o in range(len(job.ops)):
            for m in range(len(lab.machines)):
                a_mo = lab.machine_can_do_operation(lab.machines[m], job.ops[o])
                model += y[j, o, m] <= int(a_mo)

    for m in range(len(lab.machines)):
        for s in range(num_slots):
            model += lpSum(x[j, o, m, s] for j, job in enumerate(jobs) for o in range(len(job.ops))) <= 1

    for j, job in enumerate(jobs):
        for o in range(len(job.ops)):
            model += lpSum(y[j, o, m] for m in range(len(lab.machines))) == 1

    for m in range(len(lab.machines)):
        for j, job in enumerate(jobs):
            for o in range(len(job.ops)):
                model += lpSum(x[j, o, m, s] for s in range(num_slots)) == y[j, o, m]

    for (m, s) in ms:
        model += t[m, s] >= 0

    solver = PULP_CBC_CMD(msg=msg, timeLimit=400)
    model.solve(solver)
    return dict(makespan=makespan, b=b, t=t, x=x, num_slots=num_slots)