import simpy
import random
import numpy as np
import file_sys as fs

class MultiServerSystem:
    def __init__(self, env, num_servers, arrival_rate, service_rate, arrival_queue):
        self.env = env
        self.num_servers = num_servers # for printing purposes
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.arrival_queue = arrival_queue
        self.wait_times = []

    def customer(self, name, arrival_time):
        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            # print(f"{name} in system with {self.num_servers} servers, got service after waiting {wait_time:.2f} ")
            fs.write(name, arrival_time, wait_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate)
            self.wait_times.append(wait_time)
            service_time = random.expovariate(self.service_rate)
            yield self.env.timeout(service_time)

    def run(self):
        i = 0
        while True:
            arrival_time = yield self.arrival_queue.get()
            # print(f"Customer {i} in system with {self.num_servers} servers, ______________arrived at {arrival_time:.2f}")
            self.env.process(self.customer(f'Customer {i}', arrival_time))
            i += 1

def simulate_systems(num_servers_list, arrival_rate, service_rate, sim_time):
    env = simpy.Environment()
    arrival_queues = [simpy.Store(env) for _ in num_servers_list]
    systems = [MultiServerSystem(env, n, arrival_rate, service_rate, arrival_queues[i]) for i, n in enumerate(num_servers_list)]
    for system in systems:
        env.process(system.run())
    
    def generate_arrivals():
        while True:
            yield env.timeout(random.expovariate(arrival_rate))
            arrival_time = env.now
            # Put the same arrival time into each system's queue
            for queue in arrival_queues:
                yield queue.put(arrival_time)

    env.process(generate_arrivals())
    env.run(until=sim_time)
    return [system.wait_times for system in systems]

if __name__ == "__main__":
    arrival_rate = 0.9  # Lambda
    service_rate = 1.0  # Mu
    sim_time = 100  # Total simulation time

    # Simulate multiple systems with separate arrival queues
    num_servers_list = [1, 2, 4]  # Different numbers of servers
    wait_times_list = simulate_systems(num_servers_list, arrival_rate, service_rate, sim_time)
    for i, wait_times in enumerate(wait_times_list):
        mean_wait = np.mean(wait_times)
        print(f"Average waiting time for system with n={num_servers_list[i]} servers: {mean_wait:.2f}")
