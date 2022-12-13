from typing import List

'''
Base this off of the PCR workcell:
- https://github.com/AD-SDL/rpl_workcell
'''
class WorkCell:
    operations: List[Operation]
    machines: List[Machine]
    jobs: List[List]

    def __init__(self):
        self.operations_dict = {
            OpCode.Peel:     Operation(OpCode.Peel, 5, ["Peeler"]),
            OpCode.Transfer: Operation(OpCode.Transfer, 3, ["pf400"]),
            OpCode.GetPlate: Operation(OpCode.GetPlate, 6, ["sciclops"]),
            OpCode.Seal:     Operation(OpCode.Seal, 2, ["Sealer"]),
        }
        self.machines_dict = {
            "Peeler":   Machine("Peeler", ["Peel"]),
            "pf400":    Machine("pf400", ["Transfer"]),
            "sciclops": Machine("sciclops", ["GetPlate"]),
            "Sealer":   Machine("Sealer", ["Seal"]),
        }
        self.operations = self.operations_dict.values()
        self.machines = self.machines_dict.values()
        self.jobs = [
            [OpCode.Peel, OpCode.Transfer, OpCode.GetPlate],
            [OpCode.GetPlate, OpCode.Transfer, OpCode.Seal, OpCode.Transfer, OpCode.Peel]
        ]