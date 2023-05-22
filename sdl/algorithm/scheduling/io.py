from dataclasses import dataclass, field


@dataclass(frozen=True)
class SchedulingDecisions:
    makespan: int
    machine_operations: dict[tuple[int, ...], int]
    starting_times: dict[tuple[int, ...], int]
    completion_times: dict[tuple[int, ...], int]
    operation_prec: dict[tuple[int, ...], int]
    total_time: dict[int, int]
