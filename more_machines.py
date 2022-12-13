import numpy.random as random

from collections import defaultdict
from tabulate import tabulate
from pilot_demo.lab import *
from pilot_demo.opt import *


def displayMachines(machines: Machine):
    for i, machine in enumerate(machines):
        ops = {op.name for op in machine.ops}
        print(f'Machine {i} ({machine.name}) can do operations {ops}')


def displayJobs(jobs: List[Job]):
    for i, job in enumerate(jobs):
        ops = [op.name for op in job.ops]
        print(f'Job {i}-> {job.name} steps: {ops}')
        

# m machines and n jobs
def main(num_machines: int, num_jobs: int) -> None:
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
    for i in range(4, num_machines):
        m_type = random.randint(0, 3)
        new_machine = Machine(i, machs[m_type].ops, machs[m_type].name + '-' + str(i))
        total_machines.append(new_machine)
    
    
    durations = {opcode: dur for opcode, dur in enumerate([5, 3, 6, 2])}
    lab = SDLLab(total_machines, ops, durations)

    jobs = []
        # Job([ops[i] for i in [0, 1, 2]], 'job1'),
    
    for i in range(num_jobs):
        number_of_steps = random.randint(2, 6)
        operations = [ ops[random.randint(0, 3)] for j in range(number_of_steps)]
        job = Job(operations, 'job' + str(i))
        jobs.append(job)
    
    
    out = schedule(lab, jobs, msg=False)

    displayMachines(total_machines)
    displayJobs(jobs)
    
    print(f'\nMakespan: {out["makespan"].value()}\n')
    b = out["b"]
    x = out["x"]
    num_slots = sum(len(j) for j in jobs)
    table_msg = []
    header = ['job', 'operation', 'machine (name)', 'machine (id)', 'machine slot', 'begin time']    
    machine_steps = defaultdict(list)
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
                        machine_steps[m].append(the_s)
                        count += 1
            table_msg.append([
                j, op.name, the_m.name, the_m.idx, the_s, b[j, o].value()
            ])
    
    print(tabulate(table_msg, header))
    print('')
    
    for m, steps in machine_steps.items():
        has_duplicates = len(steps) == len(set(steps))
        print(f'Machine({m}): does {"NOT" if has_duplicates else ""} have duplicates! ({steps})')
    
    

if __name__ == '__main__':
    random.seed(None)
    main(20, 5)