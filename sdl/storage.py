import os.path
import pickle
from sdl.lab import SDLLab, Job, Decision
from typing import List
import pandas as pd

class Storage:
    def __init__(self, filename: str = '', csv_file: str = '', save_pkl: bool = True):
        self.pd_data_frame = None
        self.filename = filename
        self.csv_file = csv_file
        self.data = None
        self.meta_data = None
        self.save_pkl = save_pkl

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
    def set_meta_data(self, p:int, m:int, n:int, o:int, steps_min:int, steps_max:int, index: int,
                      algorithm_name: str ='unspecified'):
        self.meta_data = {
            'index': [index],
            'partitions': [p],
            'n_machines': [m],
            'n_jobs': [n],
            'n_operations': [o],
            'steps_min': [steps_min],
            'steps_max': [steps_max],
            'algorithm': [algorithm_name],
        }


    def set_makespan_genetic_history(self, history: List[int]):
        self.data['makespan_history'] = history

    def save(self):
        if self.save_pkl:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.data, f)

        self.meta_data['makespan'] = [self.data['makespan']]
        self.meta_data['runtime'] = [self.data['runtime']]
        self.data['meta_data'] = self.meta_data
        self.pd_data_frame = pd.DataFrame.from_dict(self.meta_data)
        if not os.path.exists(self.csv_file):
            self.pd_data_frame.to_csv(self.csv_file, header=True, index=False)
        else:
            with open(self.csv_file, 'a') as f:
                self.pd_data_frame.to_csv(f, header=False, index=False)

    def load(self) -> dict:
        with open(self.filename, 'rb') as f:
            self.data = pickle.load(f)
        return self.data
