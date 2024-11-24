import threading
import time
import numpy as np
import multi_server_system as mss   # Importing the multi_server_system module

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
    arrival_rate = 0.9  # Lambda
    service_rate = 1.0  # Mu
    sim_time = 10000  # Total simulation time

    # Simulate multiple systems with separate arrival queues
    num_servers_list = [1, 2, 4]  # Different numbers of servers
    wait_times_list = mss.simulate_systems(num_servers_list, arrival_rate, service_rate, sim_time)
    for i, wait_times in enumerate(wait_times_list):
        mean_wait = np.mean(wait_times)
        print(f"Average waiting time for system with n={num_servers_list[i]} servers: {mean_wait:.2f}")


def main_controller():
    while True:
        print("*" * 80)
        print("Select an option to run:")
        print("1: Run multi-server system simulation, for n=1,2,4, each system repeats 10000 times")
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
        elif choice == 0:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice, please select a valid option.")

if __name__ == "__main__":
    main_controller()

