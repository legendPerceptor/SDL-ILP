from pilot_demo.lab import Job, SDLLab
from pulp import *
from typing import List

INF = 1e18

def schedule(lab: SDLLab, jobs: List[Job]):
    # Initialize the problem itself.
    model = LpProblem('SDL-Scheduling', LpMinimize)

    # Initialize the set of indices to be used by the decision variables below.
    num_slots = sum(len(j) for j in jobs)
    jo = [(j, o) for j in range(len(jobs)) for o in range(len(jobs[j].ops))]
    ms = [(m, s) for m in range(len(lab.machines)) for s in range(num_slots)]
    joms = [(j, o, m, s) 
        for j in range(len(jobs)) for o in range(len(jobs[j].ops))
        for m in range(len(lab.machines)) for s in range(num_slots)
    ]

    # Declare/initialize the decision variables.
    makespan = LpVariable('Makespan (SP)', lowBound=0, upBound=None, cat=LpInteger)
    b = LpVariable.dicts('Beginning Operation Times', jo, lowBound=0, upBound=None, cat=LpInteger)
    t = LpVariable.dicts('Startup Times', ms, lowBound=0, upBound=None, cat=LpInteger)
    x = LpVariable.dicts('Operation-Machine Assignment', joms, cat=LpBinary)

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
        up_to_last_operation = job.ops[:-1]
        for o, op in enumerate(up_to_last_operation):
            model += b[j, o] + lab.proc_time(op.opcode) <= b[j, o + 1]

    # Constraint (c): Ensure no overlapping operations run on any one machine in a slot.
    for j, job in enumerate(jobs):
        for o in range(len(job.ops)):
            for m in range(len(lab.machines)):
                for s in range(num_slots - 1):
                    op = job.ops[o]
                    model += t[m, s] + x[j, o, m, s] * lab.proc_time(op.opcode) <= t[m, s + 1]

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
    
    # Constraint (f): ...
    for j, job in enumerate(jobs):
        for o in range(len(job.ops)):
            for m in range(len(lab.machines)):
                model += lpSum(x[j, o, m, s] for s in range(num_slots)) <= 1

    # Constraint (g): ...
    for m in range(len(lab.machines)):
        for s in range(num_slots):
            model += lpSum(x[j, o, m, s] for j, job in enumerate(jobs) for o in range(len(job.ops))) == 1

    # Constraint (h): ...
    for j, job in enumerate(jobs):
        for o in range(len(job.ops)):
            for m in range(len(lab.machines)):
                for s in range(num_slots):
                    x[j, o, m, s] <= int(lab.machine_can_do_operation(m, o))

    model.solve()

    return dict(makespan=makespan, b=b, t=t, x=x, num_slots=num_slots)