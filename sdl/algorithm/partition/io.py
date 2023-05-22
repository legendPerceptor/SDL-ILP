from dataclasses import dataclass


@dataclass(frozen=True)
class PartitionDecisions:
    matching: dict[int, set[int]]  # or `dict[SdlID, set[ExperimentID]]`
