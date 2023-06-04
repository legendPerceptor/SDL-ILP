from dataclasses import dataclass, field
from sdl.lab import MachineSchedule

@dataclass(frozen=True)
class SchedulingDecisions:
    makespan: int
    machine_operations: dict[tuple[int, ...], int]
    starting_times: dict[tuple[int, ...], int]
    completion_times: dict[tuple[int, ...], int]
    operation_prec: dict[tuple[int, ...], int]
    total_time: dict[int, int]

@dataclass(frozen=True)
class ScheduleResult:
    makespan: int
    machine_schedules: dict[int, list[MachineSchedule]]
    job_schedules: dict[int, list[tuple[int, int]]]