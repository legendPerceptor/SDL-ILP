from collections import namedtuple
from dataclasses import dataclass, field
from numpy.random import randint
from typing import List, NewType, Set, Dict, Union

Experiment = namedtuple('Experiment', [...])
MIN_DURATION = 10
MAX_DURATION = 10_000

OpCode = NewType('OpCode', int)


@dataclass(frozen=True)
class Operation:
    opcode: Union[OpCode, int]
    name: str
    duration: int = field(default=0)
    # machines: Set[int] = field(default_factory=set)


@dataclass(frozen=True)
class MachineSchedule:
    job_id: int
    job_step: int
    operation: Operation
    start_time: int
    end_time: int


@dataclass(frozen=True)
class Decision:
    job_id: int
    operation: Operation
    machine_id: int
    starting_time: int
    completion_time: int
    duration: int


@dataclass(frozen=True)
class Machine:
    idx: int
    name: str
    ops: Set[Operation]

    def has_operation(self, op: Operation) -> bool:
        return op in self.ops


@dataclass(frozen=True)
class Job:
    idx: int
    name: str
    ops: List[Operation]

    def __iter__(self) -> iter:
        return iter(self.ops)

    def __len__(self) -> int:
        return len(self.ops)


class SDLLab:
    def __init__(
            self,
            machines: List[Machine],
            operations: Set[Operation],
            durations: Dict[int, int] = None
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

        self.op_to_machine_ids: Dict[int, Set[int]] = dict()
        self.opcode_to_op: Dict[int, Operation] = dict()
        for op in operations:
            opid = op.opcode
            self.opcode_to_op[opid] = op
            for machine in self.machines:
                if op in machine.ops:
                    if opid not in self.op_to_machine_ids:
                        self.op_to_machine_ids[opid] = set()
                    self.op_to_machine_ids[opid].add(machine.idx)

    def machines_that_can_do(self, op: Operation):
        return [mach.idx for mach in self.machines
                if mach.has_operation(op)]

    def proc_time(self, opcode: OpCode) -> int:
        return self.durations[opcode]

    def can_perform(self, job: Job) -> bool:
        for op in job:
            valid_machines = self.machines_that_can_do(op)
            if len(valid_machines) == 0:
                return False
        return True

    @staticmethod
    def machine_can_do_operation(self, m: Machine, o: Operation) -> bool:
        return m.has_operation(o)
