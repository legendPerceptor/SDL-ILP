import logging
import matplotlib.pyplot as plt
import numpy.random as random
import sdl.algorithm.opt_2010 as ilp
import sdl.algorithm.list_scheduling as greedy
from sdl.random.sdl import create_sdl

from sdl.lab import *
from time import perf_counter
from typing import List, Dict
from sdl.plot import SDLPlot, plotAll, renderSchedule
from sdl.verify import ScheduleVerifier

from sdl.algorithm.genetic import schedule_from_chromosome, Chromosome, Individual, genetic_solve

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
    schedule_verifier = ScheduleVerifier(opt_schedule, lab, jobs)
    if schedule_verifier.verify_all():
        logging.info('The schedule provided by ILP is valid.')
    else:
        logging.error('The schedule provided by ILP is NOT valid.')
    # Plot the solver's decisions in MPL.
    plotAll(opt_schedule, machines, jobs, op_durations, makespan, 'ilp-schedule.png')


def genetic_main(machines: List[Machine],
                 operations: List[Operation],
                 op_durations: Dict[OpCode, int],
                 jobs: List[Job], random_state: random.RandomState):
    lab = SDLLab(machines, set(operations), op_durations)
    makespan, sjs, ms = greedy.solve(lab, jobs)
    greedy_schedule = renderSchedule(ms)
    plotAll(greedy_schedule, machines, jobs, op_durations, makespan, 'greedy-schedule-genetic.png')
    flattened_schedule = []
    machine_selection = []
    operation_sequence = []
    for job_id_1, job_decision in enumerate(sjs):
        for step in job_decision:
            flattened_schedule.append((job_id_1 + 1, step[0] + 1, step[1]))
            # step[0] is machine id - 1, step[1] is start time

    flattened_copy = flattened_schedule.copy()
    # print("flattened copy:", flattened_copy)
    for job_id, machine_id, start_time in flattened_copy:
        machine_selection.append(machine_id)
    flattened_copy = sorted(flattened_copy, key=lambda x: x[2])
    print("flattened copy:", flattened_copy)
    for job_id, machine_id, start_time in flattened_copy:
        operation_sequence.append(job_id)
        # machine_selection.append(machine_id)

    greedy_chromsome = Chromosome(machine_selection, operation_sequence)
    greedy_individual = Individual(greedy_chromsome, lab, jobs)

    # makespan2, sjs2, ms2 = schedule_from_chromosome(machine_selection, operation_sequence, lab, jobs)
    makespan2, sjs2, ms2, best_chromesome = genetic_solve(lab, jobs, random_state, [greedy_individual], 10, 5)
    reconstructed_schedule = renderSchedule(ms2)
    plotAll(reconstructed_schedule, machines, jobs, op_durations, makespan, 'reconstructed-schedule-genetic.png')
    print("sjs:", sjs)
    print("ms:", ms)
    print('-----------')
    print("reconstructed sjs:", sjs2)
    print("reconstructed ms:", ms2)
    print("makespan:", makespan)
    print("makespan2:", makespan2)


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
    logging.info(f'Time taken (in seconds) to solve the greedy schedule: {end - start}.')
    greedy_schedule = renderSchedule(ms)
    schedule_verifier = ScheduleVerifier(greedy_schedule, lab, jobs)
    if schedule_verifier.verify_all():
        logging.info('The schedule provided by Greedy Algorithm is valid.')
    else:
        logging.error('The schedule provided by Greedy Algorithm is NOT valid.')
    # Plot the solver's decisions in MPL.
    plotAll(greedy_schedule, machines, jobs, op_durations, makespan, 'greedy-schedule.png')


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


def test_sdl_factory(filename):
    random_state = random.RandomState(67)
    machines, jobs, operations, operations_to_machines = create_sdl(
        p=3, m=5, n=3, o=20, steps_min=3, steps_max=6, filename=filename, random_state=random_state)
    durations = {
        op.opcode: op.duration for op in operations
    }
    # greedy_main(machines, operations, durations, jobs, msg=True)
    # ilp_main(machines, operations, durations, jobs, msg=True)
    genetic_main(machines, operations, durations, jobs, random_state)


if __name__ == '__main__':
    # filename = 'sdl/operations.txt'
    filename = 'sdl/depr/simple_operation_names.txt'
    test_sdl_factory(filename=filename)
    # test_sdl_factory_ilp(filename=filename)
