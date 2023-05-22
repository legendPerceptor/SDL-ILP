import unittest
from sdl.lab import Operation, Job, Machine, SDLLab
# from numpy.random import RandomState
from sdl.algorithm.scheduling import list_scheduling as greedy
from sdl.algorithm import opt_2010 as ilp
from sdl.plot import renderSchedule, renderILPSchedule, plotAll


class FactoryTestCase(unittest.TestCase):
    def test_random_sdl_init(self):
        machines, jobs, operations = 0, 0, 0
        self.assertEqual(True, True)

    def test_small_greedy_not_optimal_case(self):
        operations = [Operation(1, 'A', 5), Operation(2, 'B', 4), Operation(3, 'C', 8), Operation(4, 'D', 7)]
        operation_set = set(operations)
        machines = [Machine(1, 'M1', operation_set), Machine(2, 'M2', operation_set),
                    Machine(3, 'M3', {operations[0], operations[2], operations[3]})]
        jobs = [Job(1, 'J1', [operations[0], operations[1], operations[2]]),
                Job(2, 'J2', [operations[0], operations[1], operations[3]]),
                Job(3, 'J3', [operations[1], operations[2]])]
        operations_to_machines = {op.opcode: set() for op in operations}
        operations_to_machines[operations[0].opcode] = {1, 2, 3}
        operations_to_machines[operations[1].opcode] = {1, 2}
        operations_to_machines[operations[2].opcode] = {1, 2, 3}
        operations_to_machines[operations[3].opcode] = {1, 2, 3}
        durations = {
            op.opcode: op.duration for op in operations
        }
        # random_state = RandomState(42)
        lab = SDLLab(machines, operation_set, durations)
        greedy_makespan, greedy_sjs, greedy_ms = greedy.solve(lab, jobs)
        greedy_schedule = renderSchedule(greedy_ms)
        out = ilp.solve(lab, jobs, msg=True, time_limit=50)
        ilp_makespan = out['makespan']
        ilp_schedule = renderILPSchedule(out, lab, jobs)
        plotAll(greedy_schedule, machines, jobs, durations, greedy_makespan, 'greedy_small_case.png')
        plotAll(ilp_schedule, machines, jobs, durations, ilp_makespan, 'ilp_small_case.png')
        self.assertLess(ilp_makespan, greedy_makespan)


if __name__ == '__main__':
    unittest.main()
