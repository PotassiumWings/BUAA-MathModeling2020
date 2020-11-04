import random
import copy
import matplotlib.pyplot as plt

DEBUG = False  # True for detailed logs


class Job:
    def __init__(self, arrival_time, job_id, service_rate):
        self.job_id = job_id
        self.arrival_time = arrival_time
        self.service_time = random.expovariate(service_rate)
        self.service_start_time = 0
        self.service_end_time = 0
        self.job_delay_time = 0
        self.queue_time = 0
        self.status = 0  # 0 for created, 1 for queued, 2 for processing, 3 for completed

    def add_and_process_job_queue(self, this_system):
        self.service_time = self.service_time
        self.service_start_time = max(self.arrival_time, this_system.latest_job_service_ending_time)
        self.service_end_time = self.service_start_time + self.service_time
        self.queue_time = self.service_start_time - self.arrival_time
        self.job_delay_time = self.queue_time + self.service_time


class System:
    def __init__(self, service_rate):
        self.service_rate = service_rate
        self.latest_job_service_ending_time = 0  # initially no job
        self.queue_list = []
        self.idle_time = 0
        self.current_time = 0
        self.avgCntArea = 0

    def handle_jobs(self, the_new_job=None):
        have_new_job = the_new_job is not None
        last_time = self.current_time
        if have_new_job:
            self.current_time = the_new_job.arrival_time
            if self.latest_job_service_ending_time < self.current_time:
                self.idle_time += self.current_time - self.latest_job_service_ending_time
                self.avgCntArea += (self.latest_job_service_ending_time - last_time) * len(self.queue_list)
            else:
                self.avgCntArea += max(0, self.current_time - last_time) * len(self.queue_list)
            self.latest_job_service_ending_time = the_new_job.service_end_time
        else:
            if self.queue_list[0].status < 2:
                self.current_time = self.queue_list[0].service_start_time
            else:
                self.current_time = self.queue_list[0].service_end_time
            self.avgCntArea += max(0, self.current_time - last_time) * len(self.queue_list)
            self.latest_job_service_ending_time = 1e9  # INFINITE

        finished_jobs = []
        temp_copy_of_jobs_in_sys = copy.copy(self.queue_list)

        for this_job in temp_copy_of_jobs_in_sys:
            if this_job.service_start_time <= self.current_time and this_job.status < 2:
                if DEBUG:
                    print("Time: " + "{:.4f}".format(this_job.service_start_time) + "secs \t\t"
                          "Job Id: " + str(this_job.job_id) + " Started processing ..... ")
                this_job.status = 2
                if this_job.service_end_time <= self.current_time:
                    this_job.status = 3
                    if DEBUG:
                        print("Time: " + "{:.4f}".format(this_job.service_end_time) + "secs \t\t"
                              "Job Id: " + str(this_job.job_id) + " Finished processing , queue size is: "
                              + str(len(self.queue_list) - 1))
                    self.queue_list.remove(this_job)
                    finished_jobs.append(this_job)
                else:
                    continue

            elif this_job.service_end_time <= self.current_time and this_job.status == 2:
                this_job.status = 3
                if DEBUG:
                    print("Time: " + "{:.4f}".format(this_job.service_end_time) + "secs \t\tJob Id: " + str(
                        this_job.job_id) + " Finished processing, queue size is: " + str(len(self.queue_list) - 1))
                self.queue_list.remove(this_job)
                finished_jobs.append(this_job)

        if have_new_job:
            # add current job to the system's jobs
            if len(self.queue_list) >= queue_max_length:
                print("Queue maxed, no more simulate.")
                return False
            self.queue_list.append(the_new_job)

            if DEBUG:
                print("Time: " + "{:.4f}".format(self.current_time) + "secs \t\tJob Id: " + str(
                    the_new_job.job_id) + " Entered system, system job size is: " + str(len(self.queue_list)))
            the_new_job.status = 1
        return True

    def finalize_jobs(self):
        print("finalize")
        while len(self.queue_list) > 0:
            self.handle_jobs()

        print("End of last job in the System\nSimulation summary:")


class Simulator:
    def __init__(self, arrival_rate, service_rate):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.system = System(service_rate)
        self.avgCnt = 0
        self.serverUtilRate = 0

    def run(self, job_count, queue_max_length):
        print("\nTime: 0 sec, Simulation starts for λ=" + str(self.arrival_rate) + ", μ=" + str(
            self.service_rate) + ", job_count=" + str(job_count) + ", queue_max_length=" + str(queue_max_length))
        current_time = random.expovariate(self.arrival_rate)
        this_jobs = {}  # map of id:job
        job_id = 1

        queue_maxed = False

        while job_id <= job_count:
            new_job = Job(current_time, job_id, self.system.service_rate)
            this_jobs[job_id] = new_job
            new_job.add_and_process_job_queue(self.system)

            if not self.system.handle_jobs(new_job):
                queue_maxed = True
                break
            current_time += random.expovariate(self.arrival_rate)
            job_id += 1

        if not queue_maxed:
            self.system.finalize_jobs()
        print("Total jobs: " + str(len(this_jobs)))
        return this_jobs


def plot_simulation_delay_time_per_job(jobs, arrival_rate, service_rate, sumarize):
    job_ids = [key for key in jobs]

    simulation_data = [job_ids, [jobs[job_id].job_delay_time for job_id in jobs]]

    simulation_delay_avg = sum(simulation_data[1]) / len(simulation_data[1])
    print("Average waiting time: " + str(simulation_delay_avg))
    simulation_data_delay_averages = [job_ids, [simulation_delay_avg for job_id in jobs]]

    plt.figure("Simulation result")
    this_axis = plt.subplot()
    this_axis.step(simulation_data[0], simulation_data[1], label='Simulation delay time per job id')
    this_axis.step(simulation_data_delay_averages[0], simulation_data_delay_averages[1], label='Simulation E[T]')
    this_axis.set_xlabel('Job Id')
    this_axis.set_ylabel('Delay Time (secs)')
    this_axis.legend()
    this_axis.set_title(
        "Delay time M/M/1 λ=" + "{:.2f}".format(arrival_rate) + " μ: " + "{:.2f}".format(service_rate) +
        " count: " + str(customer_count) + " max_len: " + str(queue_max_length)
    )

    sumarize[arrival_rate] = [simulation_delay_avg, 1]
    plt.show()


if __name__ == '__main__':
    summary_results = {}
    arrive_time, service_time, customer_count, queue_max_length = map(float, input().split())
    lamda = 1 / arrive_time
    mu = 1 / service_time

    simulator = Simulator(lamda, mu)
    jobs = simulator.run(customer_count, queue_max_length)

    # waiting cnt
    print("Average waiting num: " + str(simulator.system.avgCntArea / simulator.system.current_time))

    # waiting time
    plot_simulation_delay_time_per_job(jobs, lamda, mu, summary_results)

    # server rate
    print("Server usage: " + str((simulator.system.current_time - simulator.system.idle_time) / simulator.system.current_time))

