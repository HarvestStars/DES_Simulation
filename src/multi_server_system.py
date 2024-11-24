import simpy
import random
import numpy as np
import file_sys as fs

class MultiServerSystem:
    def __init__(self, env, num_servers, arrival_rate, service_rate, arrival_queue, server_queue=None):
        self.env = env
        self.num_servers = num_servers # for printing purposes
        self.server = simpy.Resource(env, capacity=num_servers)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.arrival_queue = arrival_queue

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
                fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate)
            else:
                # for SJF comparison
                _, service_time = yield self.server_queue.get()
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
        self.wait_times = []

    def run(self):
        while True:
            with self.server.request() as request:
                yield request
                (_, (customer_ID, (arrival_time, service_time))) = yield self.arrival_queue.get()
                wait_time = self.env.now - arrival_time
                self.wait_times.append(wait_time)
                fs.write(customer_ID, arrival_time, wait_time, service_time, self.num_servers, fs.SIMU_RESULT_PATH, self.arrival_rate, self.service_rate, prefix="Comparison_SJF")
                yield self.env.timeout(service_time)

def simulate_systems(num_servers_list, arrival_rate, service_rate, sim_time):
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

if __name__ == "__main__":
    arrival_rate = 0.9  # Lambda
    service_rate = 1.0  # Mu
    sim_time = 1000  # Total simulation time

    # Simulate multiple systems with separate arrival queues
    wait_times_list = simulate_sjf_system(1, arrival_rate, service_rate, sim_time)