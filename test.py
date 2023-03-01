
import logging
import matplotlib.pyplot as plt
import numpy.random as random
import sdl.algorithm.opt_2010 as ilp
import sdl.algorithm.list_scheduling as greedy
from sdl.random.sdl import SDLFactory

from sdl.lab import *
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
    out = ilp.solve(lab, jobs, msg=msg, time_limit=5)
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
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6', '#2c3e50', '#7f8c8d']
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    ax = axes[0]
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

    ax = axes[1]
    for i, job in enumerate(jobs):
        start_time = 0
        for j, op in enumerate(job.ops):
            ax.broken_barh(
                [(start_time, op_durations[op.opcode])],
                (i-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[i]
            )
            ax.text(
                start_time + op_durations[op.opcode] / 2,
                i,
                f'{i}-{j}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
            start_time += op_durations[op.opcode]
    ax.set_xlim(0, makespan)
    ax.set_xlabel('Time')
    ax.set_ylabel('Job ID')
    ax.set_title('Jobs')

    ax = axes[2]
    for i, m in enumerate(machines):
        start_time = 0
        for j, op in enumerate(m.ops):
            ax.broken_barh(
                [(start_time, op_durations[op.opcode])],
                (i-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[i]
            )
            ax.text(
                start_time + op_durations[op.opcode] / 2,
                i,
                f'{j}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
            start_time += op_durations[op.opcode]
    ax.set_xlabel('Time')
    ax.set_xlim(0, makespan)
    ax.set_ylabel('Machine ID')
    ax.set_title('Machine Capabilities')
    fig.tight_layout()
    plt.savefig('figures/ilp-Mar1.png', dpi=300)
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
    logging.info(f'Time taken (in seconds) to solve the ILP: {end - start}.')

    # Plot the solver's decisions in MPL.
    colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9',
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6', '#2c3e50', '#7f8c8d']
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    for M in Ms:
        print(M)
    ax = axes[0]
    for i, M_d in enumerate(Ms):
        for decision in M_d:
            job_id, job_step, op, start_time = decision
            run_time = op.duration
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
                f'{job_id}-{job_step}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
    ax.set_ylim(-0.5, len(machines)-0.5)
    ax.set_xlim(0, makespan)
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
                [(start_time, op_durations[op.opcode])],
                (i-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[i]
            )
            ax.text(
                start_time + op_durations[op.opcode] / 2,
                i,
                f'{i}-{j}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
            start_time += op_durations[op.opcode]
    ax.set_xlim(0, makespan)
    ax.set_xlabel('Time')
    ax.set_ylabel('Job ID')
    ax.set_title('Jobs')

    ax = axes[2]
    for i, m in enumerate(machines):
        start_time = 0
        for j, op in enumerate(m.ops):
            ax.broken_barh(
                [(start_time, op_durations[op.opcode])],
                (i-0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=colors[i]
            )
            ax.text(
                start_time + op_durations[op.opcode] / 2,
                i,
                f'{j}: {op.name}',
                fontsize=6,
                ha='center',
                va='center'
            )
            start_time += op_durations[op.opcode]
    ax.set_xlabel('Time')
    ax.set_xlim(0, makespan)
    ax.set_ylabel('Machine ID')
    ax.set_title('Machine Capabilities')
    fig.tight_layout()
    plt.savefig('figures/greedy-Mar1.png', dpi=300)
    plt.show()
    


def old_small_test():
    random.seed(123)
    operations = [
        Operation(0, 'Peel', 3),
        Operation(1, 'Transfer', 5),
        Operation(2, 'GetPlate', 7),
        Operation(3, 'Seal', 11)
    ]
    machines = [
        Machine(0, {operations[0]}, 'Peeler'),
        Machine(1, {operations[1]}, 'pf400'),
        Machine(2, {operations[2]}, 'sciclops'),
        Machine(3, {operations[3]}, 'Sealer')
    ]
    durations = {
        op.opcode: op.duration for op in operations
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

def print_sdl(machines, jobs, operations):
    print("Machines:")
    for machine in machines:
        print(machine)
    print("Jobs:")
    for job in jobs:
        print(job)
    print("Operations:")
    for operation in operations:
        print(operation)

def test_sdl_factory_greedy(filename):
    machines, jobs, operations = SDLFactory().create_sdl(
        p=5, m=8, n=10, o=20, steps_min=5, steps_max=10, filename=filename)
    durations = {
        op.opcode: op.duration for op in operations
    }
    greedy_main(machines, operations, durations, jobs, msg=True)

def test_sdl_factory_ilp(filename):
    machines, jobs, operations = SDLFactory().create_sdl(
        p=5, m=8, n=10, o=20, steps_min=5, steps_max=10, filename=filename)
    durations = {
        op.opcode: op.duration for op in operations
    }
    ilp_main(machines, operations, durations, jobs, msg=True)

if __name__ == '__main__':
    # filename = 'sdl/operations.txt'
    filename = 'sdl/depr/simple_operation_names.txt'
    # test_sdl_factory_greedy(filename=filename)
    test_sdl_factory_ilp(filename=filename)
