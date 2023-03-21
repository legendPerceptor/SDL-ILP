import matplotlib.pyplot as plt
from sdl.lab import Decision, Job, Machine, Operation
class SDLPlot:
    def __init__(self, machines, jobs, op_durations, makespan):
        self.colors = ['#1abc9c', '#f1c40f', '#f39c12', '#c0392b', '#2980b9',
              '#8e44ad', '#34495e', '#bdc3c7', '#95a5a6', '#2c3e50', '#7f8c8d']
        self.machines = machines
        self.op_durations = op_durations
        self.makespan = makespan
        self.jobs = jobs

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
                    fontsize=6,
                    ha='center',
                    va='center'
                )
                start_time += self.op_durations[op.opcode]
        ax.set_xlabel('Time')
        ax.set_xlim(0, self.makespan)
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
                    fontsize=6,
                    ha='center',
                    va='center'
                )
                start_time += self.op_durations[op.opcode]
        ax.set_xlim(0, self.makespan)
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
                fontsize=6,
                ha='center',
                va='center'
            )
        ax.set_ylim(-0.5, len(self.machines) - 0.5)
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

def plotAll(schedule, machines, jobs, op_durations, makespan, filename):
    fig, axes = plt.subplots(3, 1, figsize=(16, 9))
    sdl_plot = SDLPlot(machines, jobs, op_durations, makespan)
    sdl_plot.plotSchedule(axes[0], schedule)
    sdl_plot.plotJobs(axes[1])
    sdl_plot.plotMachines(axes[2])
    fig.tight_layout()
    plt.savefig(f'figures/{filename}', dpi=300)
    plt.show()
