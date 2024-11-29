import threading
import time
import numpy as np
import multi_server_system as mss   # Importing the multi_server_system module
import visualize_util as vu
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap

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
        wait_times_list = mss.simulate_systems_once(num_servers_list, lam, FIXED_MIU, sim_time)
        for i, wait_times in enumerate(wait_times_list):
            mean_wait = np.mean(wait_times)
            print(f"Average waiting time for system with n={num_servers_list[i]} servers: {mean_wait:.2f}")

def run_multi_CI_band():
    customers = 100
    repeats = 100  # Total simulation time
    
    plt.figure(figsize=(12, 8))
    p12 = plt.subplot(2, 1, 1)
    p12.axhline(y=1e-1, color='red', linestyle='--', label='Approx. Zero')
    p12.text(10, 1.2e-1, 'Zero (approx)', color='red')

    p14 = plt.subplot(2, 1, 2)
    p14.axhline(y=1e-1, color='red', linestyle='--', label='Approx. Zero')
    p14.text(10, 1.2e-1, 'Zero (approx)', color='red')

    for lam in LAMBDAS:
        # Simulate multiple systems with separate arrival queues
        num_servers_list = [1, 2, 4]  # Different numbers of servers
        systems_CI_bands = mss.simulate_systems_CI_band(num_servers_list, lam, FIXED_MIU, customers, repeats)

        # system_CI_bands is a dictionary with key as the number of servers and value as a tuple of 3 np.arrays
        for key, (mean_diff_waits, lower_bounds, upper_bounds) in systems_CI_bands.items():
            if key == 1:
                continue # n=1, base system, no need to compare with itself

            if key == 2:
                p = p12
            else:
                p = p14
            
            # make x labels integer
            p.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            p.plot(range(repeats), mean_diff_waits, label=f"rho={lam / FIXED_MIU}")
            p.fill_between(range(repeats), lower_bounds, upper_bounds, alpha=0.4)
            p.set_yscale('log')
            
            for i in range(repeats):
                if lower_bounds[i] <= 0 <= upper_bounds[i]:
                    p.plot(i, 0, 'ro')

            p.set_xlabel("Repeats")
            p.set_ylabel("Difference of waiting Time")
            p.set_title(f"Waiting Time Difference CI Band for system n=1 and n={key}")
            p.legend()
            p.grid()
    
    plt.savefig(f"../visualization/CI_band_plot_sys.png")
    

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
    try:
        
        while True:
            print("*" * 80)
            print("Select an option to run:")
            print("1: Run multi-server system simulation, for n=1,2,4, each system repeats 10000 times")
            print("2: Run multi-server difference waiting time vizualization")
            print("3: Run Simulation between SFJ and FIFO systems")
            print("4: Run Difference waiting time vizualization between SFJ and FIFO systems")
            print("5: Run multi-server system simulation CI band plot, for n=1,2,4, each system has 1000 customers and repeats 100 times")
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

            if choice == 5:
                wait_thread = threading.Thread(target=show_wait_message, args=("Running DES simulation for different server systems, please wait ",))
                wait_thread.start()
                run_multi_CI_band()
                stop_event.set()
                wait_thread.join()

            elif choice == 0:
                print("Exiting the program.")
                break
            else:
                print("Invalid choice, please select a valid option.")
    except KeyboardInterrupt:
        print("Exiting the program.")
        stop_event.set()
    except Exception as e:
        print(f"An error occurred: {e}")
        stop_event.set()

if __name__ == "__main__":
    main_controller()

