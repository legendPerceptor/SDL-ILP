
import logging
import matplotlib.pyplot as plt
import numpy.random as random
import pilot_demo.opt_2010 as ilp
import pilot_demo.list_scheduling as greedy

from pilot_demo.lab import *
from time import perf_counter
from typing import List, Dict

FORMAT = '(%(levelname)s) [%(asctime)s]  %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


def ilp_main(
        machines: List[Machine],
        operations: List[Operation],
        op_durations: Dict[OpCode, int],
        jobs: List[Job],
        msg: bool = False
):
    """
    Runs a simple experiment of job shop scheduling for SDL workflows. The
    resulting schedule, given directly by an ILP solver, is plotted via
    `matplotlib`.

    Parameters
    ----------
    machines : list[Machine]
        List of the machines available in the setup.
    operations : list[Operation]
        List of operations that can be done in the setup.
    op_durations : dict[OpCode, int]
        Mapping from operation codes to the length of time it takes to complete.
    number_of_jobs : int
        Number of randomly-generated jobs to generate.
    msg : bool, default=False
        Outputs the log from the ILP solver.
    """
    lab = SDLLab(machines, operations, op_durations)
    start = perf_counter()
    out = ilp.solve(lab, jobs, msg=msg)
    end = perf_counter()

    makespan = out['makespan']
    x = out['x']  # machine-operation assignments
    s = out['s']  # starting times
    c = out['c']  # completion times

    logging.info(f'Time taken (in seconds) to solve the ILP: {end - start}.')
    logging.info(f'The optimally-found makespan: {makespan}.')

    # Extract the solver's decisions for each job.
    opt_schedule = []
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            for m in lab.machines_that_can_do(op):
                if x[j, o, m] == 1:
                    opt_schedule.append({
                        'job-id': j,
                        'op-kind': op,
                        'machine-id': m,
                        'starting-time': s[j, o, m],
                        'completion-time': c[j, o, m],
                        'runtime': c[j, o, m] - s[j, o, m]
                    })

    # Plot the solver's decisions in MPL.
    colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9',
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6']
    fig, ax = plt.subplots(1, 1)
    for i, decision in enumerate(opt_schedule):
        ax.broken_barh(
            [(decision['starting-time'], decision['runtime'])],
            (decision['machine-id']-0.5, 1.0),
            alpha=0.25,
            edgecolors='black',
            facecolors=colors[decision['job-id']]
        )
        ax.text(
            decision['starting-time'] + decision['runtime'] / 2,
            decision['machine-id'],
            f'{decision["job-id"]}: {decision["op-kind"].name}',
            fontsize=6,
            ha='center',
            va='center'
        )
    ax.set_ylim(-0.5, len(machines)-0.5)
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_title('Schedule')
    ax.set_yticks([m - 0.5 for m in range(len(machines)+1)], minor=True)
    ax.set_yticks([m for m in range(len(machines))], minor=False)
    ax.grid(which='minor', linestyle='--')
    plt.show()


def greedy_main(
        machines: List[Machine],
        operations: List[Operation],
        op_durations: Dict[OpCode, int],
        jobs: List[Job],
        msg: bool = False
):
    lab = SDLLab(machines, operations, op_durations)
    
    start = perf_counter()
    makespan, SJs, Ms = greedy.solve(lab, jobs)
    end = perf_counter()
    logging.info(f'The greedily-found makespan: {makespan}.')

    # Plot the solver's decisions in MPL.
    colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9',
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6']
    fig, axes = plt.subplots(1, 2)
    for M in Ms:
        print(M)
    ax = axes[0]
    for i, M_d in enumerate(Ms):
        for decision in M_d:
            start_time = decision[2]
            run_time = durations[decision[1].opcode]
            op = operations[decision[1].opcode]
            job_id = decision[0]
            machine_id = i
            ax.broken_barh(
                [(start_time, run_time)],
                (machine_id-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[job_id]
            )
            ax.text(
                start_time + run_time / 2,
                machine_id,
                f'{job_id}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
    ax.set_ylim(-0.5, len(machines)-0.5)
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_title('Schedule')
    ax.set_yticks([m - 0.5 for m in range(len(machines)+1)], minor=True)
    ax.set_yticks([m for m in range(len(machines))], minor=False)
    ax.grid(which='minor', linestyle='--')

    ax = axes[1]
    for i, job in enumerate(jobs):
        start_time = 0
        for j, op in enumerate(job.ops):
            ax.broken_barh(
                [(start_time, durations[op.opcode])],
                (i-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[i]
            )
            ax.text(
                start_time + durations[op.opcode] / 2,
                i,
                f'{i}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
            start_time += durations[op.opcode]
    ax.set_xlabel('Time')
    ax.set_ylabel('Job ID')
    ax.set_title('Jobs')
    plt.show()


if __name__ == '__main__':
    random.seed(123)
    operations = [
        Operation(0, 'Peel'),
        Operation(1, 'Transfer'),
        Operation(2, 'GetPlate'),
        Operation(3, 'Seal')
    ]
    machines = [
        Machine(0, {operations[0]}, 'Peeler'),
        Machine(1, {operations[1]}, 'pf400'),
        Machine(2, {operations[2]}, 'sciclops'),
        Machine(3, {operations[3]}, 'Sealer')
    ]
    durations = {
        opcode: dur for opcode, dur in
         enumerate([3, 5, 7, 11])
    }

    jobs = []
    number_of_jobs=9
    for i in range(number_of_jobs):
        number_of_ops = random.randint(2, 6)
        job_ops = [random.choice(operations) for _ in range(number_of_ops)]
        job = Job(job_ops, 'job-' + str(i))
        jobs.append(job)
    print(operations)
    # ilp_main(machines, operations, durations, jobs, msg=True)
    greedy_main(machines, operations, durations, jobs, msg=True)