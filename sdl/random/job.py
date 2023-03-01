import numpy as np

from sdl.lab import Operation, Job
from typing import List


class JobFactory:
    '''Factory class for creating Job objects
    Each job has a job id, job name and a list of operations
    The operations are randomly selected from the operation set.
    '''
    def __init__(self):
        self.rs = np.random.RandomState(105)
        self.jobs = []

    def create_job(self, job_id: int, job_name: str, operations: List[Operation]) -> Job:
        return Job(job_id, job_name, operations)

    def create_job_set(self, operations: List[Operation], n: int, steps_min: int = 5, steps_max: int = 10) -> List[Job]:
        self.jobs = []
        for id in range(0, n, 1):
            n_operations = self.rs.randint(steps_min, steps_max)
            cur_operations = self.rs.choice(operations, n_operations, replace=False)
            self.jobs.append(self.create_job(id+1, f'J_{id+1}', list(cur_operations)))
        return self.jobs
