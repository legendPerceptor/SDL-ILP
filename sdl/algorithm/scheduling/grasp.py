import networkx as nx

from sdl.lab import Job, SDLLab, MachineSchedule
from typing import List
from sdl.algorithm.scheduling.genetic import find_starting_time
from sdl.algorithm.scheduling.io import ScheduleResult

from numpy import random
from matplotlib import pyplot as plt

def solve(lab: SDLLab, jobs: List[Job]):
    """This is the main function to solve the scheduling problem with disjunctive graph.
    It will call the construct phase and the local search phase.
    """
    grasp = Grasp(lab, jobs)
    return grasp.construct()

class Grasp:
    """Greedy Randomized Adaptive Search Procedure to solve the schedulind
    problem with disjunctive graph"""

    def __init__(self, sdl_lab: SDLLab, jobs: List[Job], rs: random.RandomState = random.RandomState()):
        self.sdl_lab = sdl_lab
        self.jobs = jobs
        self.Ms = None
        self.SJs = None
        self.machine_colors = ['#{:02x}{:02x}{:02x}'.format(*rs.randint(0, 256, size=3))
             for i in range(len(sdl_lab.machines)+1)]
        self.total_ops = 1  # set 1 to make the last node id in the disjunctive graph
        for j in jobs:
            self.total_ops += len(j.ops)

    def construct(self):
        """The construction phase of the disjuctive graph.
        It can also be used as a standalone greedy algorithm"""
        lab = self.sdl_lab
        jobs = self.jobs

        SJs = {job.idx: [(-1, 0) for _ in job] for job in jobs}
        Ms = {machine.idx: [] for machine in lab.machines}
        job_step_counter = {job.idx: 0 for job in jobs}
        machine_avail_time_counter = {machine.idx: 0 for machine in lab.machines}
        job_next_step_avail_time = {job.idx: 0 for job in jobs}
        job_finished = {job.idx: False for job in jobs}

        while True:
            finished_job_count = 0
            # select the next operation to minimize the increase of current makespan
            cur_makespan = max(job_next_step_avail_time)
            selected_job_id, selected_step, selected_machine, selected_start_time = -1, -1, -1, -1
            selected_job = None
            selected_machine_slot_index = -1
            next_makespan = float("inf")
            for job in jobs:
                j_id = job.idx
                if job_finished[j_id]:
                    finished_job_count += 1
                    continue
                operation = job.ops[job_step_counter[j_id]]
                usable_machine_ids = lab.op_to_machine_ids[operation.opcode]
                min_start_time, on_machine = -1, -1
                # find the best machine for the current operation
                slot_index = -1
                for machine_id in usable_machine_ids:
                    # machine_id starts from 1
                    starting_time, index = find_starting_time(Ms[machine_id], operation.duration,
                                                              job_next_step_avail_time[j_id])
                    if (min_start_time > starting_time) or min_start_time == -1:
                        min_start_time = starting_time
                        on_machine = machine_id
                        slot_index = index
                if min_start_time + operation.duration < next_makespan:
                    selected_job_id = j_id
                    selected_job = job
                    selected_step = job_step_counter[j_id]
                    selected_machine = on_machine
                    selected_machine_slot_index = slot_index
                    selected_start_time = min_start_time
                    next_makespan = min_start_time + operation.duration
            if finished_job_count == len(jobs):
                break
            SJs[selected_job_id][selected_step] = (selected_machine, selected_start_time)
            cur_op = selected_job.ops[selected_step]
            Ms[selected_machine].insert(selected_machine_slot_index,
                                        MachineSchedule(selected_job_id, selected_step, cur_op, selected_start_time,
                                                        selected_start_time + lab.durations[cur_op.opcode]))
            job_step_counter[selected_job_id] += 1
            job_next_step_avail_time[selected_job_id] = selected_start_time + lab.durations[cur_op.opcode]
            machine_avail_time_counter[selected_machine] = selected_start_time + lab.durations[cur_op.opcode]
            if job_step_counter[selected_job_id] == len(selected_job):
                job_finished[selected_job_id] = True

        makespan = max(job_next_step_avail_time)
        self.Ms = Ms
        self.SJs = SJs
        # ms_dict = {i: m for i, m in enumerate(Ms)}
        return ScheduleResult(makespan=makespan, machine_schedules=Ms, job_schedules=SJs)

    def construct_using_index(self):
        """(deprecate) The construction phase of the disjuctive graph. The function is index-based, meaning the job_id,
        machine_id are default to start at 1. It is not suitable for multi-site scheduling."""
        lab = self.sdl_lab
        jobs = self.jobs
        machines = lab.machines

        SJs = [[(-1, 0) for _ in job] for job in jobs]
        Ms = [[] for _ in range(len(lab.machines))]
        job_step_counter = [0 for _ in range(len(jobs))]
        job_next_step_avail_time = [0 for _ in range(len(jobs))]
        machine_avail_time_counter = [0 for _ in range(len(lab.machines))]
        job_finished = [False for _ in range(len(jobs))]
        while True:
            finished_job_count = 0
            # select the next operation to minimize the increase of current makespan
            cur_makespan = max(job_next_step_avail_time)
            selected_job_id, selected_step, selected_machine, selected_start_time = -1, -1, -1, -1
            selected_machine_slot_index = -1
            next_makespan = float("inf")
            for j_id, job in enumerate(self.jobs):
                if job_finished[j_id]:
                    finished_job_count += 1
                    continue
                operation = job.ops[job_step_counter[j_id]]
                usable_machine_ids = lab.op_to_machine_ids[operation.opcode]
                min_start_time, on_machine = -1, -1
                # find the best machine for the current operation
                slot_index = -1
                for machine_id in usable_machine_ids:
                    # machine_id starts from 1
                    starting_time, index = find_starting_time(Ms[machine_id - 1], operation.duration,
                                                              job_next_step_avail_time[j_id])
                    if (min_start_time > starting_time) or min_start_time == -1:
                        min_start_time = starting_time
                        on_machine = machine_id - 1
                        slot_index = index
                if min_start_time + operation.duration < next_makespan:
                    selected_job_id = j_id
                    selected_step = job_step_counter[j_id]
                    selected_machine = on_machine
                    selected_machine_slot_index = slot_index
                    selected_start_time = min_start_time
                    next_makespan = min_start_time + operation.duration
            if finished_job_count == len(jobs):
                break
            SJs[selected_job_id][selected_step] = (selected_machine, selected_start_time)
            cur_op = jobs[selected_job_id].ops[selected_step]
            Ms[selected_machine].insert(selected_machine_slot_index,
                                        MachineSchedule(selected_job_id, selected_step, cur_op, selected_start_time,
                                                        selected_start_time + lab.durations[cur_op.opcode]))
            job_step_counter[selected_job_id] += 1
            job_next_step_avail_time[selected_job_id] = selected_start_time + lab.durations[cur_op.opcode]
            machine_avail_time_counter[selected_machine] = selected_start_time + lab.durations[cur_op.opcode]
            if job_step_counter[selected_job_id] == len(jobs[selected_job_id]):
                job_finished[selected_job_id] = True

        makespan = max(job_next_step_avail_time)
        self.Ms = Ms
        self.SJs = SJs
        ms_dict = {i: m for i, m in enumerate(Ms)}
        return makespan, SJs, ms_dict

    def buildGraph(self):
        if self.Ms is None or self.SJs is None:
            print("Please run the construction phase first")
            return
        G = nx.DiGraph(directed=True)
        G.add_nodes_from([(0, {"color": "#fdcb6e", "machine": -1}),
                          (self.total_ops, {"color": "#fdcb6e", "machine": -1})])
        node_id = 1

        for job in self.jobs:
            job_id = job.idx
            prev_id = 0
            for step, op in enumerate(job.ops):
                node_color = self.machine_colors[self.SJs[job_id][step][0]]
                G.add_nodes_from([(node_id, {"color": node_color, "machine": self.SJs[job_id][step][0]})])
                G.add_weighted_edges_from([(prev_id, node_id, 1)])
                if step == len(job.ops) - 1:
                    G.add_weighted_edges_from([(node_id, self.total_ops, 1)])
                prev_id = node_id
                node_id += 1

        machine_dict = nx.get_node_attributes(G, "machine")
        print(machine_dict)
        for i in range(len(self.sdl_lab.machines)):
            nodes_cur_machine = [k for k, v in machine_dict.items() if v == i]
            num_nodes = len(nodes_cur_machine)
            for i1 in range(0, num_nodes):
                for i2 in range(i1+1, num_nodes):
                    G.add_weighted_edges_from([(nodes_cur_machine[i1], nodes_cur_machine[i2], 0.1)])
                    G.add_weighted_edges_from([(nodes_cur_machine[i2], nodes_cur_machine[i1], 0.1)])

        color_values = nx.get_node_attributes(G, "color").values()
        options = {
            'node_color': color_values,
            'with_labels': True,
            'font_color': 'white',
            'arrowstyle': '-|>',
            'arrowsize': 12,
        }
        # nx.draw(G, node_color=color_values, with_labels=True, font_color='white', arrows=True)
        nx.draw(G, arrows=True, **options)
        plt.show()

    def localSearch(self):

        pass