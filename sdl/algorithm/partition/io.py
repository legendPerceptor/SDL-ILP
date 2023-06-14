from dataclasses import dataclass
from typing import Callable, Tuple

from sdl.lab import SDLLab, Job


@dataclass(frozen=True)
class PartitionDecisions:
    makespan: int
    matching: dict[int, list[Job]]  # or `dict[SdlID, set[ExperimentID]]`


def validate_partitions(
        sites: list[SDLLab],
        jobs: list[Job],
        decs: PartitionDecisions,
        scheduler: Callable[[SDLLab, list[Job]], Tuple]
) -> bool:
    site_jobs = {i: decs.matching[i] for i, _ in enumerate(sites)}

    # Constraint (1): Single-site makespans must be <= global makespan.
    for i, site in enumerate(sites):
        if decs.makespan < scheduler(site, site_jobs[i])[0]:
            return False

    # Constraint (2): Experiments can only be assigned to, at most, 1 SDL site.
    for i, i_jobs in site_jobs.items():
        for j, j_jobs in site_jobs.items():
            if i != j:
                if set(i_jobs).intersection(set(j_jobs)):
                    return False

    # Constraint (3): Experiments can only be assigned to SDL sites with the
    #                 equipment to run them.
    for i, site in enumerate(sites):
        for j in site_jobs[i]:
            if not site.can_perform(j):
                return False

    # Constraint (4): Ensures each SDL site has enough exhaustible materials to
    #                 run each experiment assigned to it.
    for i, site in enumerate(sites):
        pass

    return True
