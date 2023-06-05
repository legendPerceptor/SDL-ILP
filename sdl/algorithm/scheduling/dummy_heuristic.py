
from sdl.lab import Job, SDLLab, Machine, Operation
from typing import List, Optional
from sdl.lab import MachineSchedule
from numpy import random
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
    machine_avail_time_counter = {machine.idx: 0 for machine in lab.machines}
    job_next_step_avail_time = {job.idx: 0 for job in jobs}
    for job in jobs:
        for step_idx, op in enumerate(job):
            usable_machines = list(lab.op_to_machine_ids[op.opcode])
            machine_id = random.choice(usable_machines)
            start_time = max(machine_avail_time_counter[machine_id], job_next_step_avail_time[job.idx])
            SJs[job.idx][step_idx] = (machine_id, start_time)
            Ms[machine_id].append(MachineSchedule(job.idx, step_idx, op, start_time,
                                                  start_time + op.duration))
            job_next_step_avail_time[job.idx] = start_time + op.duration
            machine_avail_time_counter[machine_id] = start_time + op.duration
    makespan = max(job_next_step_avail_time.values())
    return ScheduleResult(makespan=makespan, machine_schedules=Ms, job_schedules=SJs)
