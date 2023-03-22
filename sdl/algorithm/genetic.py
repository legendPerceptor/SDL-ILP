from typing import List, Dict
from sdl.lab import SDLLab, Job, Operation, Machine, MachineSchedule
from dataclasses import dataclass, field
import numpy as np


def find_starting_time(slots: List[MachineSchedule], duration, minimum):
    """Find the starting time for a job on a machine."""
    if len(slots) == 0:
        return minimum, 0
    if minimum + duration < slots[0].start_time:
        return minimum, 0
    if slots[len(slots) - 1].end_time <= minimum:
        return minimum, len(slots)
    for i in range(len(slots) - 1):
        if slots[i + 1].start_time - slots[i].end_time >= duration:
            if slots[i].end_time >= minimum:
                return slots[i].end_time, i + 1
            elif slots[i + 1].start_time - duration >= minimum:
                return minimum, i + 1
    return max(slots[len(slots) - 1].end_time, minimum), len(slots)


def schedule_from_chromosome(machine_selection, operation_sequence, lab: SDLLab, jobs: List[Job]):
    """Explain the chromosome by solving one job at a time"""
    SJs = [[(-1, 0) for _ in job] for job in jobs]
    Ms = [[] for _ in range(len(lab.machines))]
    count = 0
    map_: Dict[int, int] = {}  # job_id -> step_id

    print("machine selection:", machine_selection)
    print("operation sequence:", operation_sequence)
    makespan = 0
    for i, job in enumerate(jobs):
        for j, step in enumerate(job.ops):
            SJs[i][j] = (machine_selection[count] - 1, 0)
            count += 1
    print("Partial SJs:", SJs)
    for i, job_id in enumerate(operation_sequence):
        if job_id not in map_:
            map_[job_id] = 0
        else:
            map_[job_id] += 1
        machine_id = SJs[job_id - 1][map_[job_id]][0]  # machine_id is already the reduced 1
        if map_[job_id] > 0:
            last_step_starting_time = SJs[job_id - 1][map_[job_id] - 1][1]
            last_step_ending_time = last_step_starting_time + lab.durations[
                jobs[job_id - 1].ops[map_[job_id] - 1].opcode]
        else:
            last_step_ending_time = 0
        duration = lab.durations[jobs[job_id - 1].ops[map_[job_id]].opcode]
        starting_time, index = find_starting_time(Ms[machine_id], duration,
                                                  last_step_ending_time)
        print(
            f"job_id: {job_id}, step: {map_[job_id]}, duration: {duration}, last_step_ending_time: {last_step_ending_time}, index: {index}")
        # TODO: check job_id or job_id - 1
        ending_time = starting_time + duration
        Ms[machine_id].insert(index, MachineSchedule(job_id - 1, map_[job_id], jobs[job_id - 1].ops[map_[job_id]],
                                                     starting_time, ending_time))
        print("machine_id:", Ms[machine_id])
        SJs[job_id - 1][map_[job_id]] = (machine_id, starting_time)
        if ending_time > makespan:
            makespan = ending_time

    return makespan, SJs, Ms


@dataclass(frozen=True)
class Chromosome:
    machine_selection: List[int]
    operation_sequence: List[int]


class Individual:
    def __init__(self, chromosome: Chromosome, lab: SDLLab, jobs: List[Job]):
        self.chromosome = chromosome
        self.lab = lab
        self.jobs = jobs
        self.fitness, self.SJs, self.Ms = schedule_from_chromosome(chromosome.machine_selection,
                                                                   chromosome.operation_sequence, lab, jobs)
        self.valid = True

    def update_fitness(self):
        self.fitness, self.SJs, self.Ms = schedule_from_chromosome(self.chromosome.machine_selection,
                                                                   self.chromosome.operation_sequence, self.lab,
                                                                   self.jobs)
        self.valid = True

    @classmethod
    def create_random_chromosome(cls, lab: SDLLab, jobs: List[Job], random_state: np.random.RandomState):
        machine_selection = []
        operation_sequence = []
        for job in jobs:
            for step in job.ops:
                machine_selection.append(random_state.choice(list(lab.op_to_machine_ids[step.opcode])))
                operation_sequence.append(job.idx)
        random_state.shuffle(operation_sequence)
        return cls(Chromosome(machine_selection, operation_sequence), lab, jobs)

    def mutate_machine_selection(self, random_state: np.random.RandomState):
        """Mutate the individual."""
        index = random_state.randint(0, len(self.chromosome.machine_selection))
        count = 0
        for job in self.jobs:
            if count + len(job.ops) <= index:
                count += len(job.ops)
                continue
            else:
                print(f"index: {index}, count: {count}, len(job.ops): {len(job.ops)}, L:{len(self.chromosome.machine_selection)}")
                step = job.ops[index - count]
                self.chromosome.machine_selection[index] = random_state.choice(
                    list(self.lab.op_to_machine_ids[step.opcode]))
                self.valid = False
                return

    def mutate_operation_sequence(self, random_state: np.random.RandomState):
        """Mutate the individual."""
        index1 = random_state.randint(0, len(self.chromosome.operation_sequence))
        index2 = random_state.randint(0, len(self.chromosome.operation_sequence))
        if index1 == index2:
            return  # do not mutate
        self.chromosome.operation_sequence[index1], self.chromosome.operation_sequence[index2] = \
            self.chromosome.operation_sequence[index2], self.chromosome.operation_sequence[index1]
        self.valid = False

    @classmethod
    def ms_uniform_crossover(cls, parent1, parent2, random_state: np.random.RandomState):
        """Uniform crossover for machine selection."""
        machine_selection1 = []
        machine_selection2 = []
        for i in range(len(parent1.chromosome.machine_selection)):
            if random_state.random() < 0.5:
                machine_selection1.append(parent1.chromosome.machine_selection[i])
                machine_selection2.append(parent2.chromosome.machine_selection[i])
            else:
                machine_selection1.append(parent2.chromosome.machine_selection[i])
                machine_selection2.append(parent1.chromosome.machine_selection[i])
        return machine_selection1, machine_selection2

    @classmethod
    def os_cross_over_one(cls, parent_os_sequence, child_os_sequence, selected_sub_jobs_set):
        i, iter = 0, 0
        length = len(parent_os_sequence)
        while True:
            while iter < length and parent_os_sequence[iter] in selected_sub_jobs_set:
                iter += 1
            while i < length and child_os_sequence[i] in selected_sub_jobs_set:
                i += 1
            if i >= length or iter >= length:
                break
            child_os_sequence[i] = parent_os_sequence[iter]
            i += 1
            iter += 1
        return child_os_sequence

    @classmethod
    def os_uniform_crossover(cls, parent1, parent2, random_state: np.random.RandomState):
        """Crossover for operation sequence."""
        operation_sequence1 = parent1.chromosome.operation_sequence.copy()
        operation_sequence2 = parent2.chromosome.operation_sequence.copy()
        length = len(operation_sequence1)
        jobs = parent1.jobs
        job_number = random_state.randint(1, len(jobs) - 1)
        job_id_list = np.arange(1, len(jobs) + 1)
        selected_sub_jobs = random_state.choice(job_id_list, job_number, replace=False)
        selected_sub_jobs_set = set(selected_sub_jobs)
        selected_sub_jobs_set2 = set(job_id_list) - selected_sub_jobs_set
        operation_sequence1 = cls.os_cross_over_one(parent2.chromosome.operation_sequence, operation_sequence1,
                                                    selected_sub_jobs_set)
        operation_sequence2 = cls.os_cross_over_one(parent1.chromosome.operation_sequence, operation_sequence2,
                                                    selected_sub_jobs_set2)
        return operation_sequence1, operation_sequence2

    def mate(self, other, random_state: np.random.RandomState):
        """Mate with another individual."""
        machine_selection1, machine_selection2 = self.ms_uniform_crossover(self, other, random_state)
        operation_sequence1, operation_sequence2 = self.os_uniform_crossover(self, other, random_state)
        return Individual(Chromosome(machine_selection1, operation_sequence1), self.lab, self.jobs), \
            Individual(Chromosome(machine_selection2, operation_sequence2), self.lab, self.jobs)


def genetic_solve(lab: SDLLab, jobs: List[Job], random_state: np.random.RandomState,
                  initial_population: List[Individual] = None, population_size: int = 100,
                  max_generations: int = 1000, mutation_rate: float = 0.1, crossover_rate: float = 0.9):
    """Solve the problem using genetic algorithm."""
    if initial_population is None:
        population = [Individual.create_random_chromosome(lab, jobs, random_state) for _ in range(population_size)]
    else:
        random_populations = [Individual.create_random_chromosome(lab, jobs, random_state)
                                                for _ in range(population_size - len(initial_population))]
        initial_population.extend(random_populations)
        population = initial_population
    best_individual = min(population, key=lambda x: x.fitness)
    best_fitness = best_individual.fitness
    best_chromosome = best_individual.chromosome
    best_SJs = best_individual.SJs
    best_Ms = best_individual.Ms
    for generation in range(max_generations):
        population.sort(key=lambda x: x.fitness)
        if population[0].fitness < best_fitness:
            best_individual = population[0]
            best_fitness = best_individual.fitness
            best_chromosome = best_individual.chromosome
            best_SJs = best_individual.SJs
            best_Ms = best_individual.Ms
        new_population = []
        for i in range(population_size):
            if random_state.random() < crossover_rate:
                parent1 = population[i]
                parent2 = population[random_state.randint(0, population_size - 1)]
                child1, child2 = parent1.mate(parent2, random_state)
                new_population.append(child1)
                new_population.append(child2)
            else:
                new_population.append(population[i])
        for individual in new_population:
            if random_state.random() < mutation_rate:
                individual.mutate_machine_selection(random_state)
            if random_state.random() < mutation_rate:
                individual.mutate_operation_sequence(random_state)
        population = new_population
    return best_fitness, best_SJs, best_Ms, best_chromosome