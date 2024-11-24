import threading
import time
import numpy as np
import multi_server_system as mss   # Importing the multi_server_system module
import visualize_util as vu

# Set different lambda values and a fixed miu, to get varying rho in the simulation
FIXED_MIU = 1.0
LAMBDAS = [0.5, 0.8, 0.9, 0.95, 0.99]

stop_event = threading.Event()
def show_wait_message(msg = "Hang in there, it's almost done"):
    animation = ["", ".", "..", "..."]
    idx = 0
    while not stop_event.is_set():
        print(" " * 100, end="\r")
        print(f"{msg}{animation[idx % len(animation)]}", end="\r")
        idx += 1
        time.sleep(0.5)

def run_multi_server_system():
    sim_time = 1000  # Total simulation time

    for lam in LAMBDAS:
        # Simulate multiple systems with separate arrival queues
        num_servers_list = [1, 2, 4]  # Different numbers of servers
        wait_times_list = mss.simulate_systems(num_servers_list, lam, FIXED_MIU, sim_time)
        for i, wait_times in enumerate(wait_times_list):
            mean_wait = np.mean(wait_times)
            print(f"Average waiting time for system with n={num_servers_list[i]} servers: {mean_wait:.2f}")

def run_multi_server_system_sjf():
    sim_time = 1000  # Total simulation time

    for lam in LAMBDAS:
        # Simulate multiple systems with separate arrival queues
        num_servers = 1  # Same number of servers for both systems
        wait_times_SJF, wait_times_FIFO = mss.simulate_sjf_system(num_servers, lam, FIXED_MIU, sim_time)
        mean_wait_SJF = np.mean(wait_times_SJF)
        mean_wait_FIFO = np.mean(wait_times_FIFO)
        print(f"Average waiting time for SJF system with n={num_servers} servers: {mean_wait_SJF:.2f}, rho: {lam / FIXED_MIU}")
        print(f"Average waiting time for FIFO system with n={num_servers} servers: {mean_wait_FIFO:.2f}, rho: {lam / FIXED_MIU}")

def main_controller():
    while True:
        print("*" * 80)
        print("Select an option to run:")
        print("1: Run multi-server system simulation, for n=1,2,4, each system repeats 10000 times")
        print("2: Run multi-server difference waiting time vizualization")
        print("3: Run Simulation between SFJ and FIFO systems")
        print("4: Run Difference waiting time vizualization between SFJ and FIFO systems")
        print("0: Exit")
        
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input, please enter a number.")
            continue

        if choice == 1:
            wait_thread = threading.Thread(target=show_wait_message, args=("Running DES simulation for different server systems, please wait ",))
            wait_thread.start()
            run_multi_server_system()
            stop_event.set()
            wait_thread.join()
            
        if choice == 2:
            wait_thread = threading.Thread(target=show_wait_message, args=("Running Multi-server systems waiting time difference visulization, please wait ",))
            wait_thread.start()
            vu.visulize_all_parameters_pair_diff_waiting_time(1, 2, FIXED_MIU, LAMBDAS, "FIFO")
            stop_event.set()
            wait_thread.join()

        if choice == 3:
            wait_thread = threading.Thread(target=show_wait_message, args=("Running SJF system simulation, please wait ",))
            wait_thread.start()
            run_multi_server_system_sjf()
            stop_event.set()
            wait_thread.join()
        
        if choice == 4:
            wait_thread = threading.Thread(target=show_wait_message, args=("Running SJF system waiting time difference visulization, please wait ",))
            wait_thread.start()
            vu.visulize_all_parameters_pair_diff_waiting_time_sjf(FIXED_MIU, LAMBDAS, "SJF")
            stop_event.set()
            wait_thread.join()

        elif choice == 0:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice, please select a valid option.")

if __name__ == "__main__":
    main_controller()

