from sdl.random.machine import MachineFactory
from sdl.random.operation import OperationFactory
from sdl.random.job import JobFactory


class SDLFactory:
    def __init__(self):
        pass

    def create_sdl(self, p: int, m: int, n: int, o: int, steps_min: int, steps_max: int, filename='operations.txt'):
        '''Create o operations, p partitions, m machines, and n jobs.
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
        '''
        op_fac = OperationFactory()
        op_fac.create_operation_set(filename=filename)
        operations = list(op_fac.choose_n_operations(o))
        mc_fac = MachineFactory()
        machines = mc_fac.create_machine_partition(operations=operations, p=p, m=m)
        job_fac = JobFactory()
        jobs = job_fac.create_job_set(operations=operations, n=n, steps_min=steps_min, steps_max=steps_max)
        return machines, jobs, operations
