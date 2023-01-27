import pulp
from enum import auto, Enum
from typing import List, Dict
from sdl.env import SDLEnv

INF = 1e18

def ILP(env: SDLEnv):
    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("The Production Problem", pulp.LpMinimize)

    joms, jo, ms = set(), set(), set()
    number_of_slots = sum(len(job) for job in env.jobs)
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            ms.add((m, s))
            for j in range(len(env.jobs)):
                for o in range(len(env.jobs[j])):
                    joms.add((j, o, m, s))
                    jo.add((j, o))


    x = pulp.LpVariable.dicts('Machine-Operation Assignments', joms, cat=pulp.LpInteger)
    b = pulp.LpVariable.dicts('Operation Begin Time', jo, cat=pulp.LpInteger)
    t = pulp.LpVariable.dicts('Machine Startup Time', ms, cat=pulp.LpInteger)
    SP = pulp.LpVariable('Makespan', cat=pulp.LpInteger)
    prob += SP # The optimization goal

    # Constraint (A): Makespan must be greater than the end time of each job.
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            prob += b[j, o] + env.operations[env.jobs[j][o]].duration <= SP


    # Constraint (B): Each job must have its operation performed in order.
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j]) - 1):
            prob += b[j, o] + env.operations[env.jobs[j][o]].duration <= b[j, o + 1]

    # Constraint (C): No operation is run on a machine during a prior operation's processing time.
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            for m in range(len(env.machines)):
                for s in range(number_of_slots):
                    prob += t[m, s] + x[j, o, m, s] * env.operations[env.jobs[j][o]].duration <= t[m, s + 1]

    # Constraint (D): ...
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            for j1 in range(len(env.jobs)):
                for j2 in range(len(env.jobs)):
                    for o1 in range(len(env.jobs[j1])):
                        for o2 in range(len(env.jobs[j2])):
                            prob += t[m, s] <= b[j1, o1] + INF * (1 - x[j2, o2, m, s])

    # Constraint (E):
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            for j1 in range(len(env.jobs)):
                for j2 in range(len(env.jobs)):
                    for o1 in range(len(env.jobs[j1])):
                        for o2 in range(len(env.jobs[j2])):
                            prob += t[m, s] + INF * (1 - x[j2, o2, m, s]) >= b[j1, o1]

    # Constraint (F): ...
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            for m in range(len(env.machines)):
                prob += pulp.lpSum(x[j, o, m, s] for s in range(number_of_slots)) <= 1

    # Constraint (G): ...
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            prob += pulp.lpSum(x[j, o, m, s] for j in range(len(env.jobs)) for o in range(len(env.jobs[j]))) == 1


    # Constraint (H): ...
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            for m in range(len(env.machines)):
                for s in range(number_of_slots):
                    a_mo = int(env.machines[m] in env.operations[env.jobs[j][o]].machines)
                    prob += x[j, o, m, s] <= a_mo

    solver = pulp.PULP_CBC_CMD()
    prob.solve(solver)
    