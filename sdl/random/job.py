from numpy.random import RandomState
from sdl.lab import Operation, Job
from typing import Iterable


def random_jobs(
        num_of_jobs: int,
        operation_pool: Iterable[Operation],
        steps_min: int = 5,
        steps_max: int = 10,
        random_state: RandomState = None
) -> list[Job]:
    if random_state is None:
        random_state = RandomState()
    jobs = []
    for job_id in range(1, num_of_jobs + 1, 1):
        n_operations = random_state.randint(steps_min, steps_max)
        ops = random_state.choice(operation_pool, n_operations, replace=True)
        jobs.append(Job(job_id, f'J_{job_id}', list(ops)))
    return jobs
