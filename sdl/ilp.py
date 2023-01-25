import pulp
from enum import auto, Enum
from typing import List, Dict
from sdl.env import SDLEnv

INF = 1e18

def ILP(env: SDLEnv):
    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("The Production Problem", pulp.LpMinimize)

    jo = {(j, o) for j in range(len(env.jobs)) for o in range(len(env.jobs[j]))}
    tj = pulp.LpVariable.dicts("Joboperations", jo, cat=pulp.LpInteger)
    SP = pulp.LpVariable("The Makespan", cat=pulp.LpInteger)
    prob += SP # The optimization goal

    # use the maximum possible number of slots for every machine
    number_of_slots = sum(len(job) for job in env.jobs)

    xs = {(m, s, j, o) for m in range(len(env.machines))
         # TODO: how to define all the operations that will be run for a machine
         for s in range(number_of_slots)
         for j in range(len(env.jobs))
         for o in range(len(env.jobs[j]))}
    x = pulp.LpVariable.dicts("MachineOperations", xs, cat=pulp.LpBinary)

    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            # Constraint 1: The makespan must be greater than the end time of each job
            prob += tj[j, o] + env.operations[env.jobs[j][o]].duration <= SP
            # Constraint 2: Each job must have its operation performed in order
            if o < len(env.jobs[j]) - 1:
                prob += tj[j, o] + env.operations[env.jobs[j][o]].duration <= tj[j, o + 1]
            # Constraint 3: Each machine can only do one operation at a time
            for m in range(len(env.machines)):
                for s in range(number_of_slots):
                    for j1 in range(len(env.jobs)):
                        for o1 in range(len(env.jobs[j1])):
                            prob += tj[j, o] * x[m, s, j, o] + env.operations[env.jobs[j][o]].duration \
                                 <= x[m, s+1, j1, o1]  * tj[j1, o1] + (1-x[m, s+1, j1, o1]) * INF
    
    # Constraint 4: Each machine will at most do job j's operation o once
    for m in range(len(env.machines)):
        for j in range(len(env.jobs)):
            for o in range(len(env.jobs[j])):
                prob += pulp.lpSum(x[m, s, j, 1] for s in range(number_of_slots)) <= 1       
    
    # Constraint 5: Each operation must be done once
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            prob += pulp.lpSum(x[m, s, j, o] for j in range(len(env.jobs)) for o in range(len(env.jobs[j]))) == 1
    
    # Constraint 6: Operations can only be done on machines that are capable of doing them
    # x[m,s,j,o] <= a[m, o]
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            for m in range(len(env.machines)):
                for s in range(number_of_slots):
                    if env.machines[m] in env.operations[env.jobs[j][o]].machines:
                        prob += x[m, s, j, o] <= 1
                    else:
                        prob += x[m, s, j, o] <= 0
    
    solver = pulp.PULP_CBC_CMD()
    prob.solve(solver)
    