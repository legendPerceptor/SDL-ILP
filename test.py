import itertools
import logging
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as random
import pandas as pd

import sdl.algorithm.scheduling.opt as ilp
# import sdl.algorithm.scheduling.grasp as greedy
import sdl.algorithm.scheduling.simple_greedy as greedy
from sdl.algorithm.scheduling import dummy_heuristic

from pathlib import Path
from sdl.algorithm.scheduling.genetic import Chromosome, Individual, genetic_solve
from sdl.lab import *
from sdl.random.sdl import create_sdl
from sdl.plot import plotAll, renderSchedule
from sdl.verify import ScheduleVerifier
from sdl.storage import Storage
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
        List of operation_pool that can be done in the setup.
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
    # x = out['x']  # machine-operation assignments
    # s = out['s']  # starting times
    # c = out['c']  # completion times
    x = out.machine_operations
    s = out.starting_times
    c = out.completion_times

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


def build_greedy_individual(lab, jobs):
    greedy_result = greedy.solve(lab, jobs)
    makespan, sjs, ms = greedy_result.makespan, greedy_result.job_schedules, greedy_result.machine_schedules
    # greedy_schedule = renderSchedule(ms)
    flattened_schedule = []
    machine_selection = []
    operation_sequence = []
    for job_id, job_decision in sjs.items():
        for step in job_decision:
            flattened_schedule.append((job_id, step[0] , step[1]))
            # step[0] is machine id, step[1] is start time

    flattened_copy = flattened_schedule.copy()
    # print("flattened copy:", flattened_copy)
    for job_id, machine_id, start_time in flattened_copy:
        machine_selection.append(machine_id)
    flattened_copy = sorted(flattened_copy, key=lambda x: x[2])
    # print("flattened copy:", flattened_copy)
    for job_id, machine_id, start_time in flattened_copy:
        operation_sequence.append(job_id)
        # machine_selection.append(machine_id)

    greedy_chromsome = Chromosome(machine_selection, operation_sequence)
    greedy_individual = Individual(greedy_chromsome, lab, jobs)
    return greedy_individual


def genetic_main(
        machines: List[Machine],
        operations: List[Operation],
        op_durations: Dict[OpCode, int],
        jobs: List[Job], random_state: random.RandomState,
        storage: Storage = None
):
    lab = SDLLab(machines, set(operations), op_durations)

    # makespan2, sjs2, ms2 = schedule_from_chromosome(machine_selection, operation_sequence, lab, jobs)
    start = perf_counter()
    greedy_individual = build_greedy_individual(lab, jobs)
    makespan2, sjs2, ms2, best_chromesome, fitness_history = \
        genetic_solve(lab, jobs, random_state, initial_population=[greedy_individual], population_size=100,
                      max_generations=100)
    end = perf_counter()

    logging.info(f'The genetic algorithm found makespan: {makespan2}.')
    logging.info(f'Time taken (in seconds) to solve the genetic schedule: {end - start}.')
    reconstructed_schedule = renderSchedule(ms2)
    # plotAll(reconstructed_schedule, machines, jobs, op_durations, makespan2, 'reconstructed-schedule-genetic.png')
    if storage is not None:
        storage.set_data(lab, jobs, reconstructed_schedule, makespan2, end - start)
        storage.set_makespan_genetic_history(fitness_history)
        storage.save()
    # print("sjs:", sjs)
    # print("ms:", ms)
    # print('-----------')
    # print("reconstructed sjs:", sjs2)
    # print("reconstructed ms:", ms2)
    # print("makespan:", makespan)
    # print("makespan2:", makespan2)


def greedy_main(
        machines: List[Machine],
        operations: List[Operation],
        op_durations: Dict[OpCode, int],
        jobs: List[Job],
        random_state: random.RandomState,
        storage: Storage = None,
):
    lab = SDLLab(machines, set(operations), op_durations)
    start = perf_counter()
    result = greedy.solve(lab, jobs)
    end = perf_counter()
    makespan, sjs, ms = result.makespan, result.job_schedules, result.machine_schedules
    logging.info(f'The greedily-found makespan: {makespan}.')
    logging.info(f'Time taken (in seconds) to solve the greedy schedule: {end - start}.')
    greedy_schedule = renderSchedule(ms)
    # schedule_verifier = ScheduleVerifier(greedy_schedule, lab, jobs)
    # if schedule_verifier.verify_all():
    #     logging.info('The schedule provided by Greedy Algorithm is valid.')
    # else:
    #     logging.error('The schedule provided by Greedy Algorithm is NOT valid.')
    #     exit(1)
    # Plot the solver's decisions in MPL.
    # plotAll(greedy_schedule, machines, jobs, op_durations, makespan, 'greedy-schedule.png')
    if storage is not None:
        storage.set_data(lab, jobs, greedy_schedule, makespan, end - start)
        storage.save()


def dummy_heuristic_main(
        machines: List[Machine],
        operations: List[Operation],
        op_durations: Dict[OpCode, int],
        jobs: List[Job],
        random_state: random.RandomState,
        storage: Storage = None,
):
    lab = SDLLab(machines, set(operations), op_durations)
    start = perf_counter()
    result = dummy_heuristic.solve(lab, jobs)
    end = perf_counter()
    makespan, sjs, ms = result.makespan, result.job_schedules, result.machine_schedules
    logging.info(f'The dummy heuristic-found makespan: {makespan}.')
    logging.info(f'Time taken (in seconds) to solve the greedy schedule: {end - start}.')
    dummy_heuristic_schedule = renderSchedule(ms)
    # schedule_verifier = ScheduleVerifier(greedy_schedule, lab, jobs)
    # if schedule_verifier.verify_all():
    #     logging.info('The schedule provided by Greedy Algorithm is valid.')
    # else:
    #     logging.error('The schedule provided by Greedy Algorithm is NOT valid.')
    #     exit(1)
    # Plot the solver's decisions in MPL.
    # plotAll(greedy_schedule, machines, jobs, op_durations, makespan, 'greedy-schedule.png')
    if storage is not None:
        storage.set_data(lab, jobs, dummy_heuristic_schedule, makespan, end - start)
        storage.save()

def load_schedule_from_file(filename):
    storage = Storage(filename)
    storage.load()
    schedule = storage.data["schedule"]
    machines = storage.data["machines"]
    jobs = storage.data["jobs"]
    op_durations = storage.data["durations"]
    makespan = storage.data["makespan"]
    runtime = storage.data['runtime']
    # print("reloaded makespan:", makespan)
    # plotAll(schedule, machines, jobs, op_durations, storage.data["makespan"], 'greedy-schedule-reload.png')
    # return schedule, machines, jobs, op_durations, makespan, runtime
    return storage


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
    greedy_main(machines, operations, durations, jobs, random_state)
    # ilp_main(machines, operation_pool, durations, jobs, msg=True)
    # genetic_main(machines, operation_pool, durations, jobs, random_state)


def test_storage_plot_performance(fn, filename, csv_file):
    random_state = random.RandomState(101)
    p, m, n, o, steps_min, steps_max = 3, 5, 3, 20, 3, 6
    for i in range(10):
        machines, jobs, operations, operations_to_machines = create_sdl(
            p=p, m=m, n=n, o=o, steps_min=steps_min, steps_max=steps_max, random_state=random_state)
        durations = {
            op.opcode: op.duration for op in operations
        }
        storage = Storage(filename=filename.format(index=i), csv_file=csv_file)
        storage.set_meta_data(p, m, n, o, steps_min, steps_max, i, algorithm_name=fn.__name__)
        # greedy_main(machines, operation_pool, durations, jobs, filename=f'data/greedy_schedule_makespan-{i}.pkl')
        # genetic_main(machines, operation_pool, durations, jobs, random_state, filename=f'data/genetic_makespan-{i}.pkl')
        fn(machines, operations, durations, jobs, random_state, storage)
        p += 1
        m += 2
        n += 5
        o += 5
        steps_min += 2
        steps_max += 4


def test_sensitivity(fn, filename, csv_file):
    random_state = random.RandomState(101)
    # p, m, n, o, steps_min, steps_max = 3, 5, 3, 20, 3, 6
    i = 0
    p = 9
    for m, n, o, n_steps in itertools.product(range(10, 101, 5),
                                              range(10, 101, 5),
                                              range(10, 101, 5),
                                              range(10, 101, 5)):
        steps_min, steps_max = n_steps, n_steps + 1
        machines, jobs, operations, operations_to_machines = create_sdl(
            p=p, m=m, n=n, o=o, steps_min=steps_min, steps_max=steps_max, random_state=random_state)
        durations = {
            op.opcode: op.duration for op in operations
        }
        storage = Storage(filename=filename.format(index=i), csv_file=csv_file, save_pkl=False)
        storage.set_meta_data(p, m, n, o, steps_min, steps_max, i, algorithm_name=fn.__name__)
        # greedy_main(machines, operation_pool, durations, jobs, filename=f'data/greedy_schedule_makespan-{i}.pkl')
        # genetic_main(machines, operation_pool, durations, jobs, random_state, filename=f'data/genetic_makespan-{i}.pkl')
        fn(machines, operations, durations, jobs, random_state, storage)
        i += 1
        print('i:', i)


def load_test_storage_performance(greedy_file_template, genetic_file_template):
    greedy_stores = []
    genetic_stores = []
    for i in range(10):
        greedy_store = load_schedule_from_file(greedy_file_template.format(index=i))
        greedy_stores.append(greedy_store)
        genetic_store = load_schedule_from_file(genetic_file_template.format(index=i))
        genetic_stores.append(genetic_store)
    greedy_makespans = [store.data['makespan'] for store in greedy_stores]
    genetic_makespans = [store.data['makespan'] for store in genetic_stores]
    greedy_runtimes = [store.data['runtime'] for store in greedy_stores]
    genetic_runtimes = [store.data['runtime'] for store in genetic_stores]
    print("greedy_runtimes:", greedy_runtimes)
    print("genetic_runtimes:", genetic_runtimes)
    fig, axes = plt.subplots(1, 2)
    xx = np.arange(1, 11)
    ax = axes[0]
    ax.plot(xx, greedy_makespans, label='Greedy', linestyle='--', color='red')
    ax.plot(xx, genetic_makespans, label='Genetic', linestyle='-', color='blue')
    ax.set_xlabel('Complexity')
    ax.set_ylabel('Makespan')
    ax.legend()
    ax = axes[1]
    ax.plot(xx, greedy_runtimes, label='Greedy', linestyle='--', color='red')
    ax.plot(xx, genetic_runtimes, label='Genetic', linestyle='-', color='blue')
    ax.set_xlabel('Complexity')
    ax.set_ylabel('Runtime (s)')
    ax.legend()
    plt.tight_layout()
    plt.savefig('figures/compare_greedy_genetic_makespan-org.png', dpi=300)
    plt.show()

    fig, ax = plt.subplots(1, 1)
    xx = np.arange(1, 102)
    for i, store in enumerate(genetic_stores):
        ax.plot(xx, store.data['makespan_history'], label=f'complexity-{i + 1}')
    ax.set_xlabel('Generations')
    ax.set_ylabel('Makespan')
    ax.set_title("Genetic with Random Initialization")
    ax.legend(loc='upper center', ncol=2)
    plt.tight_layout()
    plt.savefig('figures/genetic_makespan_history-org.png', dpi=300)
    plt.show()


def compare_two_algorithm(alg1_csv_file, alg2_csv_file):
    df1 = pd.read_csv(alg1_csv_file)
    df2 = pd.read_csv(alg2_csv_file)
    alg1_makespans = df1['makespan'].values
    alg2_makespans = df2['makespan'].values
    alg1_runtimes = df1['runtime'].values
    alg2_runtimes = df2['runtime'].values
    print("alg1_runtimes:", alg1_runtimes)
    print("alg1_makespans:", alg1_makespans)
    alg1_name = df1['algorithm'].values[0]
    alg2_name = df2['algorithm'].values[0]
    fig, axes = plt.subplots(1, 2)
    xx = np.arange(1, 11)
    ax = axes[0]
    ax.plot(xx, alg1_makespans, label=alg1_name, linestyle='--', color='red')
    ax.plot(xx, alg2_makespans, label=alg2_name, linestyle='-', color='blue')
    ax.set_xlabel('Complexity')
    ax.set_ylabel('Makespan')
    ax.set_yscale('log')
    ax.legend()
    ax = axes[1]
    ax.plot(xx, alg1_runtimes, label=alg1_name, linestyle='--', color='red')
    ax.plot(xx, alg2_runtimes, label=alg2_name, linestyle='-', color='blue')
    ax.set_xlabel('Complexity')
    ax.set_ylabel('Runtime (s)')
    ax.set_yscale('log')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'figures/compare_{alg1_name}_{alg2_name}_makespan.png', dpi=300)
    plt.show()

if __name__ == '__main__':
    # filename = 'sdl/operation_pool.txt'
    optimized_genetic_filename = 'data/optimized-genetic/genetic_makespan-{index}.pkl'
    optimized_genetic_csv_file = 'data/optimized-genetic/genetic_makespan.csv'
    greedy_filename = 'data/greedy/greedy_makespan-{index}.pkl'
    greedy_csv_file = 'data/greedy/greedy_makespan.csv'

    unoptimized_genetic_filename = 'data/genetic_makespan-{index}.pkl'
    dummy_heuristic_filename = 'data/dummy_heuristic/dummy_heuristic_makespan-{index}.pkl'
    dummy_heuristic_csv_file = 'data/dummy_heuristic/dummy_heuristic.csv'

    # test_storage_plot_performance(greedy_main, filename=greedy_filename, csv_file=greedy_csv_file)
    # for n_trial in range(4):
    #     greedy_csv_file = Path(f'data/greedy/greedy_sensitivity-apr19-{n_trial}.csv')
    #     test_sensitivity(greedy_main, filename=greedy_filename, csv_file=greedy_csv_file)

    # test_storage_plot_performance(genetic_main, filename=optimized_genetic_filename,
    #                               csv_file=optimized_genetic_csv_file)
    # load_test_storage_performance(greedy_file_template=greedy_filename,
    #                               genetic_file_template=unoptimized_genetic_filename)

    test_storage_plot_performance(greedy_main, filename=greedy_filename,
                                  csv_file=greedy_csv_file)
    test_storage_plot_performance(dummy_heuristic_main, filename=dummy_heuristic_filename,
                                  csv_file=dummy_heuristic_csv_file)
    compare_two_algorithm(alg1_csv_file=greedy_csv_file, alg2_csv_file=dummy_heuristic_csv_file)

