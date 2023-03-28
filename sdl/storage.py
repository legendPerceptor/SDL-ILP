import pickle
from sdl.lab import SDLLab, Job, Decision
from typing import List
class Storage:
    def __init__(self, filename: str = ''):
        self.filename = filename
        self.data = {}

    def set_data(self, lab: SDLLab, jobs: List[Job], schedule: List[Decision], makespan: int, runtime: float):
        self.data = {
            'machines': lab.machines,
            'operations': lab.operations,
            'durations': lab.durations,
            'jobs': jobs,
            'schedule': schedule,
            'makespan': makespan,
            'runtime': runtime,
        }

    def set_makespan_genetic_history(self, history: List[int]):
        self.data['makespan_history'] = history

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load(self) -> dict:
        with open(self.filename, 'rb') as f:
            self.data = pickle.load(f)
        return self.data
