import numpy as np

from numpy.random import RandomState
from sdl.lab import Operation, Machine
from typing import List, Set, Optional


def create_machine(machine_id: int, machine_name: str, operations: Set[Operation]) -> Machine:
    return Machine(machine_id, machine_name, operations)


def create_machine_partition(operations: List[Operation], p: int, m: int,
                             random_state: Optional[RandomState] = None):
    if random_state is None:
        random_state = RandomState()
    if p > m:
        raise ValueError('Total number of machines should be larger than partition number')
    if p > len(operations):
        raise ValueError('Number of partition should be smaller than total number of operations')

    split_operations = np.array_split(operations, p)
    machines = []
    operations_to_machines = {op.opcode: set() for op in operations}
    for machine_id, operation_set in enumerate(split_operations):
        # Machine ID starts from 1 instead of 0
        machines.append(create_machine(machine_id + 1, f'M_{machine_id + 1}', set(operation_set)))
        for operation in operation_set:
            operations_to_machines[operation.opcode].add(machine_id + 1)

    remaining_machines = m - p
    for i in range(0, remaining_machines, 1):
        n_operations = random_state.randint(1, len(operations) // 2)
        cur_operations = random_state.choice(operations, n_operations, replace=False)
        machines.append(create_machine(p + 1 + i, f'M_{p + 1 + i}', set(cur_operations)))
        for operation in cur_operations:
            operations_to_machines[operation.opcode].add(p + 1 + i)
    return machines, operations_to_machines
