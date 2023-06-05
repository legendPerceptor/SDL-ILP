from collections import defaultdict
from sdl.lab import Job, SDLLab, Machine, Operation
from pulp import *
from typing import List, Optional
from sdl.lab import MachineSchedule
from sdl.algorithm.scheduling.io import SchedulingDecisions, ScheduleResult

def solve(lab: SDLLab, jobs: List[Job]):
    """
    For intance, we have the following jobs and machines:
    jobs = [J1, J2, J3, J4]
    J1 = [O1, O2, O3]
    J2 = [O4, O2, O6]
    J3 = [O7, O8, O1, O9]
    J4 = [O9, O8, O11]
    M1 = [O1, O2, O3, O4, O5, O6, O7]
    M2 = [O8, O9, O10, O11]

    The idea of list scheduling is to schedule a job's step immediately when one machine
    can do the job.
    The output will be like this. Each operation in the job is scheduled on a machine with a specific starting time.
    The makespan will be the minimum of the completion time of the last operation in each job.
    SJ[job1.idx] = [(M1, t1),(M1, t2),(M1, t3)]
    SJ[job2.idx] = [(M1, t4),(M1, t5),(M1, t6)]
    SJ[job3.idx] = [(M1, t7),(M2, t8),(M2, t9),(M2, t10)]
    SJ[job4.idx] = [(M2, t11),(M2, t12),(M2, t13)]
    Ms[m1.idx] = [(J1, O1, t1),(J2, O2, t2), ...]
    Ms[m2.idx] = [(J4, O8, t8),(J3, O9, t9), ...]
    """

    SJs = {job.idx: [(-1, 0) for _ in job] for job in jobs}
    Ms = {machine.idx: [] for machine in lab.machines}
    job_step_counter = {job.idx: 0 for job in jobs}
    machine_avail_time_counter = {machine.idx: 0 for machine in lab.machines}
    job_next_step_avail_time = {job.idx: 0 for job in jobs}
    job_finished = {job.idx: False for job in jobs}
    print("OP to Machine IDS: ", lab.op_to_machine_ids)
    while True:
        finished_job_count = 0
        for job in jobs:
            if job_finished[job.idx]:
                finished_job_count += 1
                continue
            cur_op = job.ops[job_step_counter[job.idx]]
            min_start_time, on_machine = -1, -1
            for machine_id in lab.op_to_machine_ids[cur_op.opcode]:
                # machine_id starts from 1
                if (min_start_time > machine_avail_time_counter[machine_id]) or min_start_time == -1:
                    min_start_time = max(machine_avail_time_counter[machine_id], job_next_step_avail_time[job.idx])
                    on_machine = machine_id
            SJs[job.idx][job_step_counter[job.idx]] = (on_machine, min_start_time)
            Ms[on_machine].append(MachineSchedule(job.idx, job_step_counter[job.idx], cur_op, min_start_time,
                                                  min_start_time + lab.durations[cur_op.opcode]))
            job_step_counter[job.idx] += 1
            job_next_step_avail_time[job.idx] = min_start_time + lab.durations[cur_op.opcode]
            machine_avail_time_counter[on_machine] = min_start_time + lab.durations[cur_op.opcode]
            if job_step_counter[job.idx] == len(job):
                job_finished[job.idx] = True
        if finished_job_count == len(jobs):
            break
    makespan = max(job_next_step_avail_time.values())
    return ScheduleResult(makespan=makespan, machine_schedules=Ms, job_schedules=SJs)
