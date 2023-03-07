import numpy as np

from sdl.lab import Operation, Job
from typing import List


def create_job(job_id: int, job_name: str, operations: List[Operation]) -> Job:
    return Job(job_id, job_name, operations)


def create_job_set(operations: List[Operation], num_of_jobs: int, steps_min: int = 5, steps_max: int = 10,
                   random_state: np.random.RandomState = None) -> List[Job]:
    if random_state is None:
        random_state = np.random.RandomState()
    jobs = []
    for job_id in range(1, num_of_jobs + 1, 1):
        n_operations = random_state.randint(steps_min, steps_max)
        cur_operations = random_state.choice(operations, n_operations, replace=False)
        jobs.append(create_job(job_id, f'J_{job_id}', list(cur_operations)))
    return jobs
