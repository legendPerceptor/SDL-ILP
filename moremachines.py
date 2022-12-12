import numpy.random as random


from pilot_demo.lab import *
from pilot_demo.opt import *

def displayMachines(machines : Machine):
    for i, machine in enumerate(machines):
        message = f"Machine {i}-> {machine.name} can do operations <"
        for op in machine.ops:
            message += f"{op.name}, "
        message += ">"
        print(message)

def displayJobs(jobs : List[Job]):
    for i, job in enumerate(jobs):
        message = f"Job {i}-> {job.name} steps: <"
        for op in job.ops:
            message += f"{op.name}, "
        message += ">"
        print(message)
        

# m machines and n jobs
def main(m : int, n : int) -> None:
    ops = [
        Operation(0, 'Peel'),
        Operation(1, 'Transfer'),
        Operation(2, 'GetPlate'),
        Operation(3, 'Seal')
    ]
    machs = [
        Machine(0, {ops[0]}, 'Peeler'),
        Machine(1, {ops[1]}, 'pf400'),
        Machine(2, {ops[2]}, 'sciclops'),
        Machine(3, {ops[3]}, 'Sealer')
    ]
    
    total_machines = machs.copy()
    for i in range(4, m):
        m_type = random.randint(0, 3)
        new_machine = Machine(i, machs[m_type].ops, machs[m_type].name + '-' + str(i))
        total_machines.append(new_machine)
    
    
    durations = {opcode: dur for opcode, dur in enumerate([5, 3, 6, 2])}
    lab = SDLLab(total_machines, ops, durations)

    jobs = []
        # Job([ops[i] for i in [0, 1, 2]], 'job1'),
    
    for i in range(n):
        number_of_steps = random.randint(2, 6)
        operations = [ ops[random.randint(0, 3)] for j in range(number_of_steps)]
        job = Job(operations, 'job' + str(i))
        jobs.append(job)
    
    
    out = schedule(lab, jobs)

    displayMachines(total_machines)
    displayJobs(jobs)
    print(f'Makespan: {out["makespan"].value()}')
    b = out["b"]
    x = out["x"]
    num_slots = sum(len(j) for j in jobs)
    for j, job in enumerate(jobs):
        message = ""
        for o, op in enumerate(job.ops):
            the_m, the_s = -1, -1
            count = 0
            for m, c_machine in enumerate(total_machines):
                # found = False
                for s in range(num_slots):
                    if x[j,o,m,s].value() == 1:
                        the_m, the_s = c_machine, s
                        count += 1
                        # found = True
                        # break
                # if found:
                #     break
            message += f"b[{j},{o}] {op.name} on {the_m.name} index={the_m.idx}, step {the_s}  = {b[j, o].value()}, "
        print(message)


if __name__ == '__main__':
    random.seed(None)
    main(6, 3)