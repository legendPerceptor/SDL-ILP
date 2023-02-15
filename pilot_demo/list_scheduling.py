from pilot_demo.lab import Job, SDLLab, Machine, Operation
from pulp import *
from typing import List, Optional

def solve(lab: SDLLab, jobs: List[Job]):
    '''
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
    SJ1 = [(M1, t1),(M1, t2),(M1, t3)]
    SJ2 = [(M1, t4),(M1, t5),(M1, t6)]
    SJ3 = [(M1, t7),(M2, t8),(M2, t9),(M2, t10)]
    SJ4 = [(M2, t11),(M2, t12),(M2, t13)]
    Ms1 = [(J1, O1, t1),(J2, O2, t2), ...]
    Ms2 = [(J4, O8, t8),(J3, O9, t9), ...]
    '''
    SJs = [[(-1, 0) for s in job] for job in jobs]
    Ms = [[] for _ in range(len(lab.machines))]
    job_step_counter = [0 for _ in range(len(jobs))]
    machine_avail_time_counter = [0 for _ in range(len(lab.machines))]
    job_next_step_avail_time = [0 for _ in range(len(jobs))]
    job_finished = [False for _ in range(len(jobs))]
    print("OP to Machine IDS: ", lab.op_to_machine_ids)
    while True:
        finished_job_count = 0
        for i, job in enumerate(jobs):
            if job_finished[i]:
                finished_job_count += 1
                continue
            cur_op = job.ops[job_step_counter[i]]
            min_start_time, on_machine = -1, -1
            for machine in lab.op_to_machine_ids[cur_op.opcode]:
                if (min_start_time > machine_avail_time_counter[machine]) or min_start_time == -1:
                    min_start_time = max(machine_avail_time_counter[machine], job_next_step_avail_time[i])
                    on_machine = machine
            SJs[i][job_step_counter[i]] = (on_machine, min_start_time)
            Ms[on_machine].append((i, cur_op, min_start_time))
            job_step_counter[i] += 1
            job_next_step_avail_time[i] = min_start_time + lab.durations[cur_op.opcode]
            machine_avail_time_counter[on_machine] = min_start_time + lab.durations[cur_op.opcode]
            if job_step_counter[i] == len(jobs[i]):
                job_finished[i] = True
        if finished_job_count == len(jobs):
            break
    makespan = max(machine_avail_time_counter)
    return makespan, SJs, Ms
        