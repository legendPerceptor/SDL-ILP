import numpy as np

from sdl.lab import Operation
from typing import List, Set, Optional


def create_operation(operation_id: int, operation_name: str, duration: int) -> Operation:
    return Operation(operation_id, operation_name, duration)


def create_operation_set(filename: str = None,
                         random_state: Optional[np.random.RandomState] = None) -> List[Operation]:
    if random_state is None:
        random_state = np.random.RandomState()
    if filename is None:
        operations = [f'OP_{i}' for i in range(1, 200)]
    else:
        try:
            with open(filename, 'r') as f:
                operations = f.readlines()
            # operation_pool = [op.strip() for op in operation_pool]
        except IOError as e:
            print(f'Cannot open file {filename}')
            print(e)
            return []
    result: List[Operation] = []
    for operation_id, name in enumerate(operations):
        duration = random_state.randint(5, 50)
        result.append(create_operation(operation_id + 1, name.strip(), duration))
    return result


def choose_n_operations(operations: List[Operation], n: int,
                        random_state: Optional[np.random.RandomState] = None) -> List[Operation]:
    if random_state is None:
        random_state = np.random.RandomState()
    return random_state.choice(operations, n, replace=False)
