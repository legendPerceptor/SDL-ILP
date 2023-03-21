from typing import List, Dict
from sdl.lab import SDLLab, Job, Operation, Machine, MachineSchedule


def find_starting_time(slots: List[MachineSchedule], duration, minimum):
    """Find the starting time for a job on a machine."""
    if len(slots) == 0:
        return minimum, 0
    if minimum + duration < slots[0].start_time:
        return minimum, 0
    if slots[len(slots) - 1].end_time <= minimum:
        return minimum, len(slots)
    for i in range(len(slots) - 1):
        if slots[i + 1].start_time - slots[i].end_time >= duration:
            if slots[i].end_time >= minimum:
                return slots[i].end_time, i + 1
            elif slots[i + 1].start_time - duration >= minimum:
                return minimum, i + 1
    return max(slots[len(slots) - 1].end_time, minimum), len(slots)


def schedule_from_chromosome_job_even(machine_selection, operation_sequence, lab: SDLLab, jobs: List[Job]):
    """Explain the chromosome by making the jobs even"""
    pass


def schedule_from_chromosome(machine_selection, operation_sequence, lab: SDLLab, jobs: List[Job]):
    """Explain the chromosome by solving one job at a time"""
    SJs = [[(-1, 0) for _ in job] for job in jobs]
    Ms = [[] for _ in range(len(lab.machines))]
    count = 0
    map_: Dict[int, int] = {}  # job_id -> step_id

    print("machine selection:", machine_selection)
    print("operation sequence:", operation_sequence)
    makespan = 0
    for i, job in enumerate(jobs):
        for j, step in enumerate(job.ops):
            SJs[i][j] = (machine_selection[count] - 1, 0)
            count += 1
    print("Partial SJs:", SJs)
    for i, job_id in enumerate(operation_sequence):
        if job_id not in map_:
            map_[job_id] = 0
        else:
            map_[job_id] += 1
        machine_id = SJs[job_id - 1][map_[job_id]][0]  # machine_id is already the reduced 1
        if map_[job_id] > 0:
            last_step_starting_time = SJs[job_id - 1][map_[job_id] - 1][1]
            last_step_ending_time = last_step_starting_time+lab.durations[jobs[job_id - 1].ops[map_[job_id] - 1].opcode]
        else:
            last_step_ending_time = 0
        duration = lab.durations[jobs[job_id - 1].ops[map_[job_id]].opcode]
        starting_time, index = find_starting_time(Ms[machine_id], duration,
                                                  last_step_ending_time)
        print(
            f"job_id: {job_id}, step: {map_[job_id]}, duration: {duration}, last_step_ending_time: {last_step_ending_time}, index: {index}")
        # TODO: check job_id or job_id - 1
        ending_time = starting_time + duration
        Ms[machine_id].insert(index, MachineSchedule(job_id - 1, map_[job_id], jobs[job_id - 1].ops[map_[job_id]],
                                                     starting_time, ending_time))
        print("machine_id:", Ms[machine_id])
        SJs[job_id - 1][map_[job_id]] = (machine_id, starting_time)
        if ending_time > makespan:
            makespan = ending_time

    return makespan, SJs, Ms
