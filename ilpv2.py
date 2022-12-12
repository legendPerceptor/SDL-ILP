import pulp
from enum import auto, Enum
from typing import List, Dict

INF = 1e18

class OpCode(Enum):
    Peel = auto()
    Transfer = auto()
    GetPlate = auto()
    Seal = auto()


class Operation:
    def __init__(self, name, duration, machines):
        self.name = name
        self.duration = duration
        self.machines = machines

    # TODO: Parameterize this so that the duration is a function of the current state of the SDL space.
    # def duration(self, params):
    #     return self.duration(params)

class Machine:
    def __init__(self, name, operations):
        self.name = name
        self.operations = operations

class Environment:
    operations: List[Operation]
    machines: List[Machine]
    jobs: List[List]

    def __init__(self):
        self.operations_dict = {
            OpCode.Peel: Operation(OpCode.Peel, 5, ["Peeler"]),
            OpCode.Transfer: Operation(OpCode.Transfer, 3, ["pf400"]),
            OpCode.GetPlate: Operation(OpCode.GetPlate, 6, ["sciclops"]),
            OpCode.Seal: Operation(OpCode.Seal, 2, ["Sealer"]),
        }
        self.machines_dict = {
            "Peeler": Machine("Peeler", ["Peel"]),
            "pf400": Machine("pf400", ["Transfer"]),
            "sciclops": Machine("sciclops", ["GetPlate"]),
            "Sealer": Machine("Sealer", ["Seal"]),
        }
        self.operations = list(self.operations_dict.values())
        self.machines = list(self.machines_dict.values())
        self.jobs = [
            [OpCode.Peel, OpCode.Transfer, OpCode.GetPlate],
            [OpCode.GetPlate, OpCode.Transfer, OpCode.Seal, OpCode.Transfer, OpCode.Peel]
        ]

def ILP(env: Environment):
    # Create the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("The Production Problem", pulp.LpMinimize)

    jo = {(j, o) for j in range(len(env.jobs)) for o in range(len(env.jobs[j]))}
    number_of_slots = sum(len(job) for job in env.jobs)
    ms = {(m, s) for m in range(len(env.machines)) for s in range(number_of_slots)}
    b = pulp.LpVariable.dicts("Joboperations", jo, cat=pulp.LpInteger)
    t = pulp.LpVariable.dicts("MachineSlots", ms, cat=pulp.LpInteger)
    SP = pulp.LpVariable("The Makespan", cat=pulp.LpInteger)
    prob += SP # The optimization goal

    # use the maximum possible number of slots for every machine
    

    xs = {(m, s, j, o) for m in range(len(env.machines))
         # TODO: how to define all the operations that will be run for a machine
         for s in range(number_of_slots)
         for j in range(len(env.jobs))
         for o in range(len(env.jobs[j]))}
    x = pulp.LpVariable.dicts("MachineOperations", xs, cat=pulp.LpBinary)

    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            # Constraint 1a: The makespan must be greater than the end time of each job
            prob += b[(j, o)] + env.operations_dict[env.jobs[j][o]].duration <= SP

    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):        
            # Constraint 1b: Each job must have its operation performed in order
            if o < len(env.jobs[j]) - 1:
                prob += b[(j, o)] + env.operations_dict[env.jobs[j][o]].duration <= b[(j, o + 1)]
    
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            for j in range(len(env.jobs)):
                for o in range(len(env.jobs[j])):
                    # Constraint 1c: Each machine can only do one operation at a time
                    if s < number_of_slots - 1:
                        prob += t[(m, s)] +  x[(m, s, j, o)] * env.operations_dict[env.jobs[j][o]].duration <= t[(m, s+1)]
                        
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            for j in range(len(env.jobs)):
                for o in range(len(env.jobs[j])):                
                    # Constraint 1d&&1e: t_m,s == b_j,o if job j's operation o is done on machine m at slot s
                    prob += t[(m, s)] <= b[(j, o)] + (1 - x[(m, s, j, o)]) * INF
                    prob += t[(m, s)] + (1 - x[(m, s, j, o)]) * INF >= b[(j, o)]
    
    # Constraint 1f: Each machine will at most do job j's operation o once
    for m in range(len(env.machines)):
        for j in range(len(env.jobs)):
            for o in range(len(env.jobs[j])):
                prob += pulp.lpSum(x[(m, s, j, o)] for s in range(number_of_slots)) <= 1       
    
    # Constraint 1g: Each operation must be done once
    for m in range(len(env.machines)):
        for s in range(number_of_slots):
            prob += pulp.lpSum(x[(m, s, j, o)] for j in range(len(env.jobs)) for o in range(len(env.jobs[j]))) == 1
    
    # Constraint 6: Operations can only be done on machines that are capable of doing them
    # x[m,s,j,o] <= a[m, o]
    for j in range(len(env.jobs)):
        for o in range(len(env.jobs[j])):
            for m in range(len(env.machines)):
                for s in range(number_of_slots):
                    if env.machines[m].name in env.operations_dict[env.jobs[j][o]].machines:
                        prob += x[(m, s, j, o)] <= 1
                    else:
                        prob += x[(m, s, j, o)] <= 0
    
    solver = pulp.PULP_CBC_CMD()
    prob.solve(solver)
    return SP, b, t
    
if __name__ == '__main__':
    env = Environment()
    print("Start solving ILP")
    SP, b ,t = ILP(env)
    print("ILP result: ", SP, b, t)
    print(f"The Makespan : {SP.value()}")
