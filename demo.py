import numpy.random as random


from sdl.lab import *
from sdl.opt import *

def main() -> None:
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
    durations = {opcode: dur for opcode, dur in enumerate([5, 3, 6, 2])}
    lab = SDLLab(machs, ops, durations)

    jobs = [
        Job([ops[i] for i in [0, 1, 2]], 'job1'),
        Job([ops[i] for i in [2, 1, 3, 1, 0]], 'job2'),
        Job([ops[i] for i in [0, 1, 2, 3, 0]], 'job3'),
        Job([ops[i] for i in [0, 1, 2, 2, 2]], 'job4'),
    ]
    
    out = schedule(lab, jobs)
    print(f'Makespan: {out["makespan"].value()}')
    b = out["b"]
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            print(f"b[{j},{o}] = {b[j, o].value()}")


if __name__ == '__main__':
    random.seed(None)
    main()