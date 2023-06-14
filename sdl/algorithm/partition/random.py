from numpy.random import RandomState
from sdl.algorithm.partition.io import PartitionDecisions, validate_partitions
from sdl.algorithm.scheduling.io import SchedulingDecisions
from sdl.lab import Job, SDLLab
from typing import Callable, Optional, Tuple


def random_partition(
        sites: list[SDLLab],
        jobs: list[Job],
        scheduler: Callable[[SDLLab, list[Job]], Tuple],
        msg: bool = False,
        limit: Optional[int] = None,
        time_limit: Optional[int] = None,
        random_state: Optional[RandomState] = None
) -> PartitionDecisions:
    if random_state is None:
        random_state = RandomState()

    valid_sites_for_jobs = {
        job_id: [site_id for site_id, site in enumerate(sites) if site.can_perform(job)]
        for job_id, job in enumerate(jobs)
    }
    partitions = {site_id: [] for site_id, _ in enumerate(sites)}
    for job_id in valid_sites_for_jobs:
        site_id = random_state.choice(valid_sites_for_jobs[job_id])
        partitions[site_id].append(jobs[job_id])

    makespan = max(scheduler(site, partitions[site_id])[0] for site_id, site in enumerate(sites))
    decs = PartitionDecisions(makespan=makespan, matching=partitions)
    if not validate_partitions(sites, jobs, decs, scheduler):
        raise ValueError("Invalid partition decisions that do not follow necessary constraints.")
    return decs
