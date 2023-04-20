import matplotlib.pyplot as plt
import matplotlib
from sdl.lab import Decision, Job, Machine, Operation
import numpy as np

def generate_colors(num_colors):
    random_state = np.random.RandomState(120)
    colors = ['#{:02x}{:02x}{:02x}'.format(*random_state.randint(0, 256, size=3)) for _ in range(num_colors)]
    return colors

class SDLPlot:
    def __init__(self, machines, jobs, op_durations, makespan):
        self.colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9',
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6', '#2c3e50', '#7f8c8d']
        if len(jobs) > 11:
            self.colors.extend(generate_colors(len(jobs) - 11))
        self.machines = machines
        self.op_durations = op_durations
        self.makespan = makespan
        self.jobs = jobs
        length = 0
        for i, m in enumerate(self.machines):
            total_length = 0
            for j, op in enumerate(m.ops):
                total_length += self.op_durations[op.opcode]
            if total_length > length:
                length = total_length
        self.length = max(length, self.makespan)

    def plotMachines(self, ax):
        for i, m in enumerate(self.machines):
            start_time = 0
            for j, op in enumerate(m.ops):
                ax.broken_barh(
                    [(start_time, self.op_durations[op.opcode])],
                    (i - 0.5, 1.0),
                    alpha=0.25,
                    edgecolors='black',
                    facecolors=self.colors[i]
                )
                ax.text(
                    start_time + self.op_durations[op.opcode] / 2,
                    i,
                    f'{j}: {op.name}',
                    fontsize=10,
                    ha='center',
                    va='center'
                )
                start_time += self.op_durations[op.opcode]
        ax.set_xlabel('Time')
        ax.set_xlim(0, self.length)
        ax.set_ylabel('Machine ID')
        ax.set_title('Machine Capabilities')

    def plotJobs(self, ax):
        for i, job in enumerate(self.jobs):
            start_time = 0
            for j, op in enumerate(job.ops):
                ax.broken_barh(
                    [(start_time, self.op_durations[op.opcode])],
                    (i - 0.5, 1.0),
                    alpha=0.25,
                    edgecolors='black',
                    facecolors=self.colors[i]
                )
                ax.text(
                    start_time + self.op_durations[op.opcode] / 2,
                    i,
                    f'{i}-{j}: {op.name}',
                    fontsize=10,
                    ha='center',
                    va='center'
                )
                start_time += self.op_durations[op.opcode]
        ax.set_xlim(0, self.length)
        ax.set_xlabel('Time')
        ax.set_ylabel('Job ID')
        ax.set_title('Jobs')

    def plotSchedule(self, ax, schedule):
        for i, decision in enumerate(schedule):
            ax.broken_barh(
                [(decision.starting_time, decision.duration)],
                (decision.machine_id - 0.5, 1.0),
                alpha=0.25,
                edgecolors='black',
                facecolors=self.colors[decision.job_id]
            )
            ax.text(
                decision.starting_time + decision.duration / 2,
                decision.machine_id,
                f'{decision.job_id}: {decision.operation.name}',
                fontsize=10,
                ha='center',
                va='center'
            )
        ax.set_ylim(-0.5, len(self.machines) - 0.5)
        ax.set_xlim(0, self.length)
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Schedule')
        ax.set_yticks([m - 0.5 for m in range(len(self.machines) + 1)], minor=True)
        ax.set_yticks([m for m in range(len(self.machines))], minor=False)
        ax.grid(which='minor', linestyle='--')

def renderSchedule(ms):
    schedule = []
    for i, M_d in enumerate(ms):
        for decision in M_d:
            # job_id, job_step, op, start_time, end_time = decision
            run_time = decision.operation.duration
            machine_id = i
            schedule.append(
                Decision(
                    job_id=decision.job_id,
                    operation=decision.operation,
                    machine_id=machine_id,
                    starting_time=decision.start_time,
                    completion_time=decision.end_time,
                    duration=run_time
                )
            )
    return schedule

def renderILPSchedule(out, lab, jobs):
    x = out['x']  # machine-operation assignments
    s = out['s']  # starting times
    c = out['c']  # completion times
    opt_schedule = []
    for j, job in enumerate(jobs):
        for o, op in enumerate(job.ops):
            for m in lab.machines_that_can_do(op):
                if x[j, o, m] == 1:
                    opt_schedule.append(Decision(
                        job_id=j,
                        operation=op,
                        machine_id=m - 1,  # for plotting, the machine id is actually the real id - 1
                        starting_time=s[j, o, m],
                        completion_time=c[j, o, m],
                        duration=c[j, o, m] - s[j, o, m]
                    ))
    return opt_schedule

def plotAll(schedule, machines, jobs, op_durations, makespan, filename):
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    matplotlib.rcParams['font.size'] = 16
    sdl_plot = SDLPlot(machines, jobs, op_durations, makespan)
    sdl_plot.plotSchedule(axes[0], schedule)
    sdl_plot.plotJobs(axes[1])
    sdl_plot.plotMachines(axes[2])
    fig.tight_layout()
    plt.savefig(f'figures/{filename}', dpi=300)
    plt.show()
