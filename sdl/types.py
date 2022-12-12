from enum import auto, Enum


class OpCode(Enum):
    Peel = auto()
    Transfer = auto()
    GetPlate = auto()
    Seal = auto()


class Operation:
    def __init__(self, name, duration, machines):
        self.name = name
        self.duration = duration
        self.machines = machines

    # TODO: Parameterize this so that the duration is a function of the current state of the SDL space.
    # def duration(self, params):
    #     return self.duration(params)

class Machine:
    def __init__(self, name, operations):
        self.name = name
        self.operations = operations
