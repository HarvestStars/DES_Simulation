import simpy
import random
import numpy as np
import file_sys as fs
from scipy import stats

class MultiServerSystem:
    def __init__(self, env, num_servers, arrival_rate, service_rate, arrival_queue, server_queue=None):
        self.env = env
        self.num_servers = num_servers # for printing purposes
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.arrival_queue = arrival_queue
        self.need_to_write = True

        if server_queue is None:
            self.server_queue = None
        else:
            self.server_queue = server_queue

        self.wait_times = []

    def customer(self, customer_ID, arrival_time):
        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)

            service_time = 0
            if self.server_queue is None:
                service_time = random.expovariate(self.service_rate)
                if self.need_to_write:
                    fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate)
            else:
                # for SJF comparison
                _, service_time = yield self.server_queue.get()
                if self.need_to_write:
                    fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate, prefix="Comparison_FIFO")
            
            yield self.env.timeout(service_time)

    def run(self):
        while True:
            customer_ID, arrival_time = yield self.arrival_queue.get()
            self.env.process(self.customer(customer_ID, arrival_time))

class MultiServerSystemSJF:
    def __init__(self, env, num_servers, arrival_rate, service_rate, arrival_queue):
        self.env = env
        self.num_servers = num_servers # for printing purposes
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.arrival_queue = arrival_queue
        self.need_to_write = True
        self.wait_times = []
        

    def run(self):
        while True:
            with self.server.request() as request:
                yield request
                (_, (customer_ID, (arrival_time, service_time))) = yield self.arrival_queue.get()
                wait_time = self.env.now - arrival_time
                self.wait_times.append(wait_time)
                if self.need_to_write:
                    fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate, prefix="Comparison_SJF")
                yield self.env.timeout(service_time)

def simulate_systems_once(num_servers_list, arrival_rate, service_rate, sim_time):
    env = simpy.Environment()
    arrival_queues = [simpy.Store(env) for _ in num_servers_list]
    systems = [MultiServerSystem(env, n, arrival_rate, service_rate, arrival_queues[i]) for i, n in enumerate(num_servers_list)]
    for system in systems:
        env.process(system.run())
    
    def generate_arrivals():
        customer_ID = 0
        while True:
            yield env.timeout(random.expovariate(arrival_rate))
            arrival_time = env.now
            # Put the same arrival time into each system's queue
            for queue in arrival_queues:
                yield queue.put((customer_ID, arrival_time))
            customer_ID += 1

    env.process(generate_arrivals())
    env.run(until=sim_time)
    return [system.wait_times for system in systems]

def simulate_systems_CI_band(num_servers_list, arrival_rate, service_rate, customers, repeats=10):
    # for each system, new a list to store the 3 np.array, the mean waiting time, the 95% lower bound and the upper bound
    Diff_CI_results = {}
    for n in num_servers_list:
        Diff_CI_results[n] = [ [], [], [] ]

    for _ in range(repeats):
        mean_waits = {}
        for n in num_servers_list:
            mean_waits[n] = []

        env = simpy.Environment()
        arrival_queues = [simpy.Store(env) for _ in num_servers_list]
        systems = [MultiServerSystem(env, n, arrival_rate, service_rate, arrival_queues[i]) for i, n in enumerate(num_servers_list)]
        for system in systems:
            system.need_to_write = False
            env.process(system.run())
        
        def generate_arrivals():
            customer_ID = 0
            while customer_ID < customers:
                yield env.timeout(random.expovariate(arrival_rate))
                arrival_time = env.now
                # Put the same arrival time into each system's queue
                for queue in arrival_queues:
                    yield queue.put((customer_ID, arrival_time))
                customer_ID += 1

        env.process(generate_arrivals())
        env.run()
        
        # need to clean the evn?
        env = None

        for system in systems: 
            # store the mean waiting time, the 95% CI lower bound and the upper bound
            wait_times = np.array(system.wait_times)
            mean_waits[system.num_servers] = wait_times

        # calculate the waiting time difference between 1 and 2, and 1 and 4,
        # then calculate the 95% confidence interval for the difference
        for i in range(1, len(num_servers_list)):

            # align the waiting times
            mean_waits[num_servers_list[i]] = mean_waits[num_servers_list[i]][:len(mean_waits[num_servers_list[0]])]
            diff = np.array(mean_waits[num_servers_list[0]]) - np.array(mean_waits[num_servers_list[i]])
            # print(f'Difference in waiting time for n={num_servers_list[0]} and n={num_servers_list[i]}: {diff}')    
            mean_diff = np.mean(diff)
            std_error = np.std(diff, ddof=1) / np.sqrt(len(diff))
            lamb_CI = stats.norm.ppf((1 + 0.95) / 2) # for 95% it should be 1.96
            
            # if bound element is NAN or INF, replace it with 0
            upper_bound = mean_diff + lamb_CI * std_error 
            lower_bound = mean_diff - lamb_CI * std_error
            if np.isnan(upper_bound) or np.isinf(upper_bound):
                upper_bound = 0
            if np.isnan(lower_bound) or np.isinf(lower_bound):
                lower_bound = 0

            Diff_CI_results[num_servers_list[i]][0].append(mean_diff)
            Diff_CI_results[num_servers_list[i]][1].append(lower_bound)
            Diff_CI_results[num_servers_list[i]][2].append(upper_bound)

    print(f'Waiting time CI bands for rho={arrival_rate / service_rate}: {Diff_CI_results}')
    return Diff_CI_results

def simulate_sjf_system(num_servers, arrival_rate, service_rate, sim_time):
    env = simpy.Environment()
    arrival_queue_SJF = simpy.PriorityStore(env) # for SJF
    arrival_queue_FIFO = simpy.Store(env) # for FIFO
    server_queue_FIFO = simpy.Store(env) # for FIFO

    system_SJF = MultiServerSystemSJF(env, num_servers, arrival_rate, service_rate, arrival_queue_SJF)
    system_FIFO = MultiServerSystem(env, num_servers, arrival_rate, service_rate, arrival_queue_FIFO, server_queue_FIFO)
    env.process(system_SJF.run())
    env.process(system_FIFO.run())

    def generate_arrivals():
        customer_ID = 0
        while True:
            yield env.timeout(random.expovariate(arrival_rate))
            arrival_time = env.now
            service_time = random.expovariate(service_rate)
            yield arrival_queue_SJF.put((service_time, (customer_ID, (arrival_time, service_time))))  # Use service_time as priority
            yield arrival_queue_FIFO.put((customer_ID, arrival_time))
            yield server_queue_FIFO.put((customer_ID, service_time))
            customer_ID += 1

    env.process(generate_arrivals())
    env.run(until=sim_time)
    
    return system_SJF.wait_times, system_FIFO.wait_times

def simulate_sjf_system_once(num_servers, arrival_rate, service_rate, customers):
    env = simpy.Environment()
    arrival_queue_SJF = simpy.PriorityStore(env) # for SJF
    arrival_queue_FIFO = simpy.Store(env) # for FIFO
    server_queue_FIFO = simpy.Store(env) # for FIFO

    system_SJF = MultiServerSystemSJF(env, num_servers, arrival_rate, service_rate, arrival_queue_SJF)
    system_SJF.need_to_write = False
    system_FIFO = MultiServerSystem(env, num_servers, arrival_rate, service_rate, arrival_queue_FIFO, server_queue_FIFO)
    system_FIFO.need_to_write = False

    env.process(system_SJF.run())
    env.process(system_FIFO.run())

    def generate_arrivals():
        customer_ID = 0
        while customer_ID < customers:
            yield env.timeout(random.expovariate(arrival_rate))
            arrival_time = env.now
            service_time = random.expovariate(service_rate)
            yield arrival_queue_SJF.put((service_time, (customer_ID, (arrival_time, service_time))))  # Use service_time as priority
            yield arrival_queue_FIFO.put((customer_ID, arrival_time))
            yield server_queue_FIFO.put((customer_ID, service_time))
            customer_ID += 1

    env.process(generate_arrivals())
    env.run()
    
    return system_SJF.wait_times, system_FIFO.wait_times

def simulate_systems_CI_band_SJF(num_servers_list, arrival_rate, service_rate, customers, repeats=10):
    results = [[],[],[]]
    for _ in range(repeats):
        sjf_waiting_time,  FIFO_waiting_time= simulate_sjf_system_once(num_servers_list, arrival_rate, service_rate, customers)
        # calculate the waiting time difference between SJF and FIFO
        # then calculate the 95% confidence interval for the difference
        diff = np.array(FIFO_waiting_time) - np.array(sjf_waiting_time)
        mean_diff = np.mean(diff)
        std_error = np.std(diff, ddof=1) / np.sqrt(len(diff))
        lamb_CI = stats.norm.ppf((1 + 0.95) / 2)
        upper_bound = mean_diff + lamb_CI * std_error
        lower_bound = mean_diff - lamb_CI * std_error
        #print(f'Difference in waiting time for SJF and FIFO: {diff}')
        #print(f'95% CI for the difference: ({lower_bound}, {upper_bound})')
        results[0].append(mean_diff)
        results[1].append(lower_bound)
        results[2].append(upper_bound)
    return results

class MultiServerSystemWithSepecialServiceRate:
    def __init__(self, env, num_servers, arrival_rate, arrival_queue, special_service_rate):
        self.env = env
        self.num_servers = num_servers # for printing purposes
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.special_service_rate = special_service_rate

        if special_service_rate == "constant":
            self.constant_service_time = 1.0
        elif special_service_rate == "long_tail":
            self.long_tail_service_rates = [
                (0.75, 1.0),  # 75%
                (0.25, 5.0)   # 25%
            ]
        else:
            self.constant_service_time = 1.0

        self.arrival_queue = arrival_queue
        self.need_to_write = True
        self.wait_times = []

    def customer(self, customer_ID, arrival_time):
        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)

            service_time = 0

            # Generate service time based on the special service rate
            if self.special_service_rate == "constant":
                # M/D/n, service time is constant
                service_time = self.constant_service_time
            elif self.special_service_rate == "long_tail":
                # M/G/n with long tail distribution
                p = random.random() # 0 ~ 1
                if p < 0.75:
                    service_time = random.expovariate(1 / self.long_tail_service_rates[0][1])  # average value is 1.0
                else:
                    service_time = random.expovariate(1 / self.long_tail_service_rates[1][1])  # average value is 5.0

            if self.need_to_write:
                fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate)

            yield self.env.timeout(service_time)

    def run(self):
        while True:
            customer_ID, arrival_time = yield self.arrival_queue.get()
            self.env.process(self.customer(customer_ID, arrival_time))


def simulate_special_service_systems_CI_band(num_servers_list, arrival_rate, customers, repeats=10, special_service_rate="constant"):
    # for each system, new a list to store the 3 np.array, the mean waiting time, the 95% lower bound and the upper bound
    Diff_CI_results = {}
    for n in num_servers_list:
        Diff_CI_results[n] = [ [], [], [] ]

    for _ in range(repeats):
        mean_waits = {}
        for n in num_servers_list:
            mean_waits[n] = []

        env = simpy.Environment()
        arrival_queues = [simpy.Store(env) for _ in num_servers_list]
        systems = [MultiServerSystemWithSepecialServiceRate(env, n, arrival_rate, arrival_queues[i], special_service_rate) for i, n in enumerate(num_servers_list)]
        for system in systems:
            system.need_to_write = False
            env.process(system.run())
        
        def generate_arrivals():
            customer_ID = 0
            while customer_ID < customers:
                yield env.timeout(random.expovariate(arrival_rate))
                arrival_time = env.now
                # Put the same arrival time into each system's queue
                for queue in arrival_queues:
                    yield queue.put((customer_ID, arrival_time))
                customer_ID += 1

        env.process(generate_arrivals())
        env.run()
        
        # need to clean the evn?
        env = None

        for system in systems: 
            # store the mean waiting time, the 95% CI lower bound and the upper bound
            wait_times = np.array(system.wait_times)
            mean_waits[system.num_servers] = wait_times

        # calculate the waiting time difference between 1 and 2, and 1 and 4,
        # then calculate the 95% confidence interval for the difference
        for i in range(1, len(num_servers_list)):

            # align the waiting times
            mean_waits[num_servers_list[i]] = mean_waits[num_servers_list[i]][:len(mean_waits[num_servers_list[0]])]
            diff = np.array(mean_waits[num_servers_list[0]]) - np.array(mean_waits[num_servers_list[i]])
            # print(f'Difference in waiting time for n={num_servers_list[0]} and n={num_servers_list[i]}: {diff}')    
            mean_diff = np.mean(diff)
            std_error = np.std(diff, ddof=1) / np.sqrt(len(diff))
            lamb_CI = stats.norm.ppf((1 + 0.95) / 2) # for 95% it should be 1.96
            
            # if bound element is NAN or INF, replace it with 0
            upper_bound = mean_diff + lamb_CI * std_error 
            lower_bound = mean_diff - lamb_CI * std_error
            if np.isnan(upper_bound) or np.isinf(upper_bound):
                upper_bound = 0
            if np.isnan(lower_bound) or np.isinf(lower_bound):
                lower_bound = 0

            Diff_CI_results[num_servers_list[i]][0].append(mean_diff)
            Diff_CI_results[num_servers_list[i]][1].append(lower_bound)
            Diff_CI_results[num_servers_list[i]][2].append(upper_bound)

    print(f'Waiting time CI bands for {special_service_rate}: {Diff_CI_results}')
    return Diff_CI_results

if __name__ == "__main__":
    arrival_rate = 0.9  # Lambda
    service_rate = 1.0  # Mu
    sim_time = 1000  # Total simulation time

    # Simulate multiple systems with separate arrival queues
    wait_times_list = simulate_sjf_system(1, arrival_rate, service_rate, sim_time)