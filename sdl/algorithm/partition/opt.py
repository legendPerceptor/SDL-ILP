from pulp import *
from sdl.algorithm.scheduling.io import SchedulingDecisions
from sdl.lab import Job, SDLLab
from typing import Callable, Optional, Tuple


def single_site_makespan(
        scheduler: Callable[[SDLLab, list[Job]], Tuple],
        site_id: int,
        site: SDLLab,
        jobs: list[Job],
        partition_decisions: LpVariable.dicts
):
    i = site_id
    site_jobs = [
        job
        for j, job in enumerate(jobs)
        if partition_decisions[i, j].value() == 1
    ]
    return scheduler(site, site_jobs)[0]  # TODO: Make the Tuple to be SchedulingDecisions


def opt_partition(
        sites: list[SDLLab],
        jobs: list[Job],
        scheduler: Callable[[SDLLab, list[Job]], Tuple],
        msg: bool = False,
        limit: Optional[int] = None,
        time_limit: Optional[int] = None
):
    if limit is None:
        limit = 1_000_000

    # Initialize the ILP and its decision variables.
    model = LpProblem('SDL-Partitioning', LpMinimize)
    ie = [(i, e) for i in range(len(sites)) for e in range(len(jobs))]
    makespan = LpVariable("Makespan", lowBound=0, upBound=None, cat=LpContinuous)
    z = LpVariable.dicts("Partition Assignment", indices=ie, cat=LpBinary)

    # Initialize the objective function.
    model += makespan

    # Constraint (1): Single-site makespans must be <= makespan decision variable.
    for i, site in enumerate(sites):
        model += single_site_makespan(scheduler, i, site, jobs, z) <= makespan

    # Cosntraint (2): Experiments can only be assigned to, at most, 1 SDL site.
    for e in range(len(jobs)):
        model += lpSum(z[i, e] for i in range(len(sites))) <= 1

    # Constraint (3): Experiments can only be assigned to SDL sites with the equipment to run them.
    for i, site in enumerate(sites):
        for e, exp in enumerate(jobs):
            model += z[i, e] <= int(site.can_perform(exp))

    # Constraint (4): Ensures each SDL site has enough exhaustible materials to run each experiment assigned to it.
    # for i, site in enumerate(sites):
    #     pass  # TODO

    return (
        makespan.value(),
        {key: z[key].value() for key in z}
    )
