import logging
import matplotlib.pyplot as plt
import numpy.random as random
import sdl.algorithm.opt_2010 as ilp
import sdl.algorithm.list_scheduling as greedy
from sdl.random.sdl import create_sdl

from sdl.lab import *
from time import perf_counter
from typing import List, Dict
from sdl.plot import SDLPlot

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
    jobs : int
        Number of randomly-generated jobs to generate.
    msg : bool, default=False
        Outputs the log from the ILP solver.
    """
    lab = SDLLab(machines, set(operations), op_durations)
    start = perf_counter()
    out = ilp.solve(lab, jobs, msg=msg, time_limit=50)
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
                    opt_schedule.append(Decision(
                        job_id=j,
                        operation=op,
                        machine_id=m,
                        starting_time=s[j, o, m],
                        completion_time=c[j, o, m],
                        duration=c[j, o, m] - s[j, o, m]
                    ))

    # Plot the solver's decisions in MPL.
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    sdl_plot = SDLPlot(machines, jobs, op_durations, makespan)
    sdl_plot.plotSchedule(axes[0], opt_schedule)
    sdl_plot.plotJobs(axes[1])
    sdl_plot.plotMachines(axes[2])
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
    lab = SDLLab(machines, set(operations), op_durations)

    start = perf_counter()
    makespan, sjs, ms = greedy.solve(lab, jobs)
    end = perf_counter()
    logging.info(f'The greedily-found makespan: {makespan}.')
    logging.info(f'Time taken (in seconds) to solve the ILP: {end - start}.')

    opt_schedule = []
    for i, M_d in enumerate(ms):
        for decision in M_d:
            job_id, job_step, op, start_time = decision
            run_time = op_durations[op.opcode]
            machine_id = i
            opt_schedule.append(
                Decision(
                    job_id=job_id,
                    operation=op,
                    machine_id=machine_id,
                    starting_time=start_time,
                    completion_time=start_time + run_time,
                    duration=run_time
                )
            )
    # Plot the solver's decisions in MPL.
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    sdl_plot = SDLPlot(machines, jobs, op_durations, makespan)
    sdl_plot.plotSchedule(axes[0], opt_schedule)
    sdl_plot.plotJobs(axes[1])
    sdl_plot.plotMachines(axes[2])
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
        Machine(0, 'Peeler', {operations[0]}),
        Machine(1, 'pf400', {operations[1]}),
        Machine(2, 'sciclops', {operations[2]}),
        Machine(3, 'Sealer', {operations[3]})
    ]
    durations = {
        op.opcode: op.duration for op in operations
    }

    jobs = []
    number_of_jobs = 9
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
    random_state = random.RandomState(123)
    machines, jobs, operations = create_sdl(
        p=5, m=8, n=10, o=20, steps_min=5, steps_max=10, filename=filename, random_state=random_state)
    durations = {
        op.opcode: op.duration for op in operations
    }
    greedy_main(machines, operations, durations, jobs, msg=True)


def test_sdl_factory_ilp(filename):
    random_state = random.RandomState(123)
    machines, jobs, operations = create_sdl(
        p=5, m=8, n=10, o=20, steps_min=5, steps_max=10, filename=filename, random_state=random_state)
    durations = {
        op.opcode: op.duration for op in operations
    }
    ilp_main(machines, operations, durations, jobs, msg=True)


if __name__ == '__main__':
    # filename = 'sdl/operations.txt'
    filename = 'sdl/depr/simple_operation_names.txt'
    # test_sdl_factory_greedy(filename=filename)
    test_sdl_factory_ilp(filename=filename)
