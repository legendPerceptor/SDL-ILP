import sdl.random.machine as machine_factory
import sdl.random.operation as operation_factory
import sdl.random.job as job_factory
import numpy as np
from typing import Optional


def create_sdl(p: int, m: int, n: int, o: int, steps_min: int, steps_max: int, filename=None,
               random_state: Optional[np.random.RandomState] = None):
    """Create o operations, p partitions, m machines, and n jobs.
    Example: o = 10, p = 4, m = 6, n = 5
    operations = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10]
    p = 4 means separate the above operations set into 4 partitions
    And the first 4 machines will ensure each operation can be done on at least one machine
    M1-M4: [o1, o4, o7], [o2, o8], [o3, o9], [o5, o6, o10]
    m = 6 means we need 2 more machines that can do some operations
    M5 = [o1, o5, o8, o9]
    M6 = [o4, o5, o7, o8]
    These additional machines will influence the schedule and they can possibly reduce the total makespan.
    Each job can have step_min to step_max operations
    """
    operation_set = operation_factory.create_operation_set(filename=filename, random_state=random_state)
    operations = list(operation_factory.choose_n_operations(operation_set, o, random_state))
    machines, operations_to_machines = machine_factory.create_machine_partition(operations=operations,
                                                                                p=p, m=m, random_state=random_state)
    jobs = job_factory.create_job_set(operations=operations, num_of_jobs=n, steps_min=steps_min,
                                      steps_max=steps_max, random_state=random_state)
    return machines, jobs, operations, operations_to_machines
