import numpy.random as random
import numpy as np
import pandas as pd

from collections import defaultdict
from tabulate import tabulate
from sdl.lab import *
from sdl.opt import *
import time
import matplotlib.pyplot as plt

class OperationSchedule:
    def __init__(self, job_index: int, op: Operation, machine: Machine, step: int, start: int, duration: int):
        self.job_index = job_index
        self.op = op
        self.machine = machine
        self.step = step
        self.start = start
        self.duration = duration


def displayMachines(machines: Machine):
    for i, machine in enumerate(machines):
        ops = {op.name for op in machine.ops}
        print(f'Machine {i} ({machine.name}) can do operations {ops}')


def displayJobs(jobs: List[Job]):
    for i, job in enumerate(jobs):
        ops = [op.name for op in job.ops]
        print(f'Job {i}-> {job.name} steps: {ops}')
        

def visualize_schedule(
        operation_schedules: List[OperationSchedule],
        total_machines: List[Machine],
        sp: int
):
    colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9', '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6']
    fig, ax = plt.subplots(1, 1)
    for i, op_schedule in enumerate(operation_schedules):
        print(f'{i}: {op_schedule.start=}, {op_schedule.duration=} '
              f'[machine={op_schedule.machine.idx}, job={op_schedule.job_index}, slot={op_schedule.step}]')
        ax.broken_barh(
            [(op_schedule.start, op_schedule.duration)],
            (op_schedule.machine.idx, 1),
            alpha=0.25,
            edgecolors='black',
            facecolors=colors[op_schedule.job_index]
        )
        ax.text(
            op_schedule.start + op_schedule.duration / 2,
            op_schedule.machine.idx + 0.5,
            f'{op_schedule.job_index}:{op_schedule.op.name}',
            ha='center',
            va='center'
        )
    ax.set_ylim(0, len(total_machines)+1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    # ax.set_yticklabels([machine.name for machine in total_machines])
    ax.set_title('Schedule')
    plt.show()


# m machines and n jobs
def main(num_machines: int, num_jobs: int):
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
    
    
    durations = {opcode: dur for opcode, dur in enumerate([8, 13, 18, 25])}
    lab = SDLLab(total_machines, ops, durations)

    jobs = []
        # Job([ops[i] for i in [0, 1, 2]], 'job1'),
    
    for i in range(num_jobs):
        number_of_ops = 4  # random.randint(2, 6)
        operations = [
            random.choice(ops) for _ in range(number_of_ops)
        ]
        job = Job(operations, 'job' + str(i))
        jobs.insert(0, job)
    
    start = time.perf_counter()
    out = schedule(lab, jobs, msg=False)
    end = time.perf_counter()
    print(f'It took {end - start} seconds to solve with ILP.')
    displayMachines(total_machines)
    displayJobs(jobs)
    
    print(f'\nMakespan: {out["makespan"].value()}\n')
    b = out["b"]
    x = out["x"]
    t = out["t"]
    num_slots = sum(len(j) for j in jobs)
    table_msg = []
    header = ['job', 'operation', 'machine (name)', 'machine (id)', 'machine slot', 'slot time (t)', 'begin time (b)', 'x[j,o,m,s]']    
    machine_steps = defaultdict(list)

    all_ms_pairs = []
    final_schedule = []

    table_header = ['machine'] + [f'slot={s}' for s in range(num_slots)]
    table = []

    for m, machine in enumerate(total_machines):
        machine_table_row = [m] + [None] * num_slots
        for s in range(num_slots):
            machine_slot_value = 0
            for j, job in enumerate(jobs):
                for o, op in enumerate(job.ops):
                    if x[j, o, m, s].value() == 1:
                        final_schedule.append(OperationSchedule(
                            j, op, machine, s, b[j, o].value(), durations[op.opcode]
                        ))
                        machine_slot_value += 1
            machine_table_row[s + 1] = machine_slot_value
        table.append(machine_table_row)

    print(tabulate(table, headers=table_header))


    # for j, job in enumerate(jobs):
    #     message = ""
    #     for o, op in enumerate(job.ops):
    #         the_m, the_s = -1, -1
    #         count = 0
    #         for m, c_machine in enumerate(total_machines):
    #             # found = False
    #             for s in range(num_slots):
    #                 if x[j, o, m, s].value() == 1:
    #                     the_m, the_s = c_machine, s
    #                     machine_steps[m].append(the_s)
    #                     all_ms_pairs.append((m, s))
    #                     count += 1
    #         if count == 1:
    #             final_schedule.append(
    #                 OperationSchedule(j, op, the_m, the_s, b[j, o].value(), durations[op.opcode])
    #             )
    #             table_msg.append([
    #                 j, op.name, the_m.name, the_m.idx, the_s,
    #                 t[the_m.idx, the_s].value(), b[j, o].value(),
    #                 x[j, o, the_m.idx, the_s].value()
    #             ])

    # for m, c_machine in enumerate(total_machines):
    #     message = f'>>> MACHINE {m}:  '
    #     for s in range(num_slots):
    #         if (m, s) in all_ms_pairs:
    #             message += f't[{m}, {s}]={t[m, s].value()},  '
    #         # else:
    #         #     message += f'{m}:{s} | {t[m,s].value()}, '
    #     print(message.strip()[:-1])

    # print(tabulate(table_msg, header))
    # print('')
    visualize_schedule(final_schedule, total_machines, out["makespan"].value())
    
    # for m, steps in machine_steps.items():
    #     has_duplicates = len(steps) == len(set(steps))
    #     print(f'Machine({m}): does {"NOT" if has_duplicates else ""} have duplicates! ({steps})')
    return out["makespan"].value(), end - start
    
    
def test_and_plot():
    n_machine_list = np.arange(5, 30, 5)
    n_job_list = np.arange(1, 30, 1)
    
    for number_of_machines in n_machine_list:
        solve_time_list = []
        make_span_list = []
        total_time_list = []
        for number_of_jobs in n_job_list:
            start = time.perf_counter()
            sp, solve_time = main(number_of_machines, number_of_jobs)
            end = time.perf_counter()
            print(f'Number of machines: {number_of_machines}, number of jobs: {number_of_jobs}, '
                  f'makespan: {sp}, solve time: {solve_time}, total time: {end - start}')
            solve_time_list.append(solve_time)
            total_time_list.append(end - start)
            make_span_list.append(sp)
        n_machines = [number_of_machines] * len(n_job_list)
        print('saving data for ', number_of_machines, ' machines')
        plot_df = pd.DataFrame(
            data = { 'solve_time': solve_time_list,
            'total_time': total_time_list, 'makespan': make_span_list,
            'n_jobs': n_job_list, 'n_machines': n_machines}
        )
        plot_df.to_csv(f'./data/{number_of_machines}_machines.csv', index=False)
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        ax[0].plot(n_job_list, solve_time_list, 'o-', color='#f39c12',label='solve time')
        ax[0].set_xlabel('Number of jobs')
        ax[0].set_ylabel('Solve Time (s)')
        ax[0].set_title(f'{number_of_machines} machines')
        ax[1].plot(n_job_list, make_span_list, 'o-', color='#2980b9',label='makespan')
        ax[1].set_xlabel('Number of jobs')
        ax[1].set_ylabel('Makespan (s)')
        plt.savefig(f'./figures/{number_of_machines}_machines.png')    


if __name__ == '__main__':
    random.seed(1)
    main(1, 2)