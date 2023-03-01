import numpy as np

from numpy.random import RandomState
from sdl.lab import Operation, Machine
from typing import List, Optional


class MachineFactory:
    '''Factory class for creating Machine objects
    We ensure each operation can be done by at least one machine.
    This is done by creating a partition of operations and assign each partition to a machine.
    There can be more machines than partitions, in which case, the additional machines can be used for any random operations.
    '''
    def __init__(self):
        self.rs = np.random.RandomState(101)
        self.machines = []

    def create_machine(self, machine_id: int, machine_name: str, operations: List[Operation]) -> Machine:
        return Machine(machine_id, machine_name, operations)

    def create_machine_partition(self, operations: List[Operation], p: int, m: int,
                       random_state: Optional[RandomState] = None):
        if random_state is None:
            random_state = RandomState()
        if p > m:
            raise ValueError('Total number of machines should be larger than partition number')
        if p > len(operations):
            raise ValueError('Number of partition should be smaller than total number of operations')

        split_operations = np.array_split(operations, p)
        self.machines = []
        for id, operation_set in enumerate(split_operations):
            self.machines.append(self.create_machine(id+1, f'M_{id+1}', set(operation_set)))

        remaining_machines = m - p
        for i in range(0, remaining_machines, 1):
            n_operations = random_state.randint(1, len(operations) // 2)
            cur_operations = random_state.choice(operations, n_operations, replace=False)
            self.machines.append(self.create_machine(p+1+i, f'M_{p+1+i}', set(cur_operations)))
        return self.machines
