import unittest
from sdl.lab import Operation, Job, Machine, SDLLab

# from numpy.random import RandomState
from sdl.algorithm.scheduling import simple_greedy as greedy
from sdl.algorithm.scheduling import dummy_heuristic

from numpy.random import RandomState

from sdl.algorithm.scheduling import opt as ilp
from sdl.algorithm.scheduling.grasp import Grasp
from sdl.plot import renderSchedule, renderILPSchedule, plotAll
from sdl.algorithm.partition.opt import opt_partition

def smallSDLInPaper():
    operations = [Operation(1, 'A', 5), Operation(2, 'B', 4), Operation(3, 'C', 8), Operation(4, 'D', 7)]
    operation_set = set(operations)
    machines = [Machine(1, 'M1', operation_set), Machine(2, 'M2', operation_set),
                Machine(3, 'M3', {operations[0], operations[2], operations[3]})]
    jobs = [Job(1, 'J1', [operations[0], operations[1], operations[2]]),
            Job(2, 'J2', [operations[0], operations[1], operations[3]]),
            Job(3, 'J3', [operations[1], operations[2]])]
    durations = {
        op.opcode: op.duration for op in operations
    }
    # random_state = RandomState(42)
    lab = SDLLab(machines, operation_set, durations)
    return lab, jobs, machines, durations, operations

def smallSDLForPartition():
    operations = [Operation(1, 'A', 5), Operation(2, 'B', 4), Operation(3, 'C', 8), Operation(4, 'D', 7),
                  Operation(5, 'E', 6), Operation(6, 'F', 14)]
    operation_set = set(operations)
    machines = [Machine(1, 'M1', {operations[1], operations[0]}), Machine(2, 'M2', operation_set),
                Machine(3, 'M3', {operations[0], operations[2], operations[3]}),
                Machine(4, 'M4', {operations[4], operations[5]})]
    jobs = [Job(4, 'J4', [operations[4], operations[5], operations[2]]),
            Job(5, 'J5', [operations[0], operations[1], operations[4]])]
    durations = {
        op.opcode: op.duration for op in operations
    }
    # random_state = RandomState(42)
    lab = SDLLab(machines, operation_set, durations)
    return lab, jobs, machines, durations, operations

class FactoryTestCase(unittest.TestCase):
    def test_random_sdl_init(self):
        machines, jobs, operations = 0, 0, 0
        self.assertEqual(True, True)

    def test_small_greedy_not_optimal_case(self):
        lab, jobs, machines, durations, operations = smallSDLInPaper()
        greedy_result = greedy.solve(lab, jobs)
        greedy_schedule = renderSchedule(greedy_result.machine_schedules)
        out = ilp.solve(lab, jobs, msg=True, time_limit=50)
        ilp_makespan = out.makespan
        ilp_schedule = renderILPSchedule(out, lab, jobs)
        plotAll(greedy_schedule, machines, jobs, durations, greedy_result.makespan, 'greedy_small_case.png')
        plotAll(ilp_schedule, machines, jobs, durations, ilp_makespan, 'ilp_small_case.png')
        self.assertLess(ilp_makespan, greedy_result.makespan)
    def test_simple_graph_in_grasp(self):
        lab, jobs, machines, durations, operations = smallSDLInPaper()
        rs = RandomState(47)
        grasp = Grasp(sdl_lab=lab, jobs=jobs, rs=rs)
        result = grasp.construct()
        grasp_makespan, grasp_sjs, grasp_ms = result.makespan, result.job_schedules, result.machine_schedules
        grasp_schedule = renderSchedule(grasp_ms)
        plotAll(grasp_schedule, machines, jobs, durations, grasp_makespan, 'grasp_small_case.png')
        grasp.buildGraph()

    def test_dummy_heuristics(self):
        lab, jobs, machines, durations, operations = smallSDLInPaper()
        result = dummy_heuristic.solve(lab, jobs)
        grasp_schedule = renderSchedule(result.machine_schedules)
        plotAll(grasp_schedule, machines, jobs, durations, result.makespan, 'dummy_heuristic_small_case.png')


    def test_partition_basic(self):
        # lab, jobs, machines, durations, operations = smallSDLInPaper()
        # lab2, jobs2, machines2, durations2, operations2 = smallSDLForPartition()
        # all_jobs = jobs + jobs2
        # labs = [lab, lab2]
        # scheduler = greedy.solve
        # partition_result = opt_partition(labs, all_jobs, scheduler)
        # print(partition_result)
        pass


if __name__ == '__main__':
    unittest.main()
