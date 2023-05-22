from itertools import groupby


class ScheduleVerifier:
    def __init__(self, schedule, lab, jobs):
        self.schedule = schedule
        self.lab = lab
        self.jobs = jobs

    def verify_job_steps(self):
        """Verify that each job has the correct steps in the correct order."""
        sorted_schedule = sorted(self.schedule, key=lambda x: (x.job_id, x.starting_time))
        for job_id, job_group in groupby(sorted_schedule, key=lambda x: x.job_id):
            job = self.jobs[job_id]
            job_steps = list(job_group)
            if len(job_steps) != len(job):
                return False
            for i, op in enumerate(job):
                if job_steps[i].operation != op:
                    return False
        return True

    def verify_machine_availabilities(self):
        """Verify that each machine is available when it is scheduled."""
        sorted_schedule = sorted(self.schedule, key=lambda x: (x.machine_id, x.starting_time))
        for machine_id, machine_group in groupby(sorted_schedule, key=lambda x: x.machine_id):
            machine_steps = list(machine_group)
            for i in range(len(machine_steps) - 1):
                if machine_steps[i].completion_time > machine_steps[i + 1].starting_time:
                    return False
        return True

    def verify_all(self):
        return self.verify_job_steps() and self.verify_machine_availabilities()

