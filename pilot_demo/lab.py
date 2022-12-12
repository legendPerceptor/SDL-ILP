from collections import namedtuple
from dataclasses import dataclass, field
from numpy.random import randint

Experiment = namedtuple('Experiment', [...])
MIN_DURATION = 10
MAX_DURATION = 10_000

@dataclass(frozen=True)
class Machine:
    idx: int
    ops: set[int]
    name: str = field(default='N/A')

    def has_operation(self, op) -> bool:
        return op in self.ops

@dataclass(frozen=True)
class Job:
    ops: list[int]
    name: str = field(default='N/A')

    def __iter__(self) -> iter:
        return iter(self.ops)

    def __len__(self) -> int:
        return len(self.ops)

@dataclass(frozen=True)
class Operation:
    opcode: int
    name: str = field(default='N/A')

class SDLLab:
    def __init__(
        self, 
        machines: list[Machine], 
        operations: set[Operation],
        durations: dict[int, int] = None
    ) -> None:
        self.machines = machines
        self.operations = operations
        if durations is None:
            self.durations = {
                op.opcode: randint(MIN_DURATION, MAX_DURATION)
                for op in operations
            }
        else:
            self.durations = durations

    def machine_can_do_operation(self, m: int, o: int) -> bool:
        return self.machines[m].has_operation(o)

    def proc_time(self, opcode: int) -> int:
        return self.durations[opcode]
