import matplotlib.pyplot as plt
import file_sys as fs
import numpy as np

def plot_pair_waiting_time_diff(n0, n1, rho, waiting_times_diff, filename_prefix):
    plt.figure(figsize=(10, 6))
    plt.xlabel("Customer Number")
    plt.ylabel("Waiting Time Difference")
    plt.title(f"Difference in Waiting Time for Customers in Two Systems, with n={n0} and n={n1} servers")
    plt.plot(waiting_times_diff, label=f"n={n0} - n={n1}")
    plt.legend()
    plt.grid()

    # check if the directory exists
    if not fs.check_directory(fs.SIMU_VISUALIZATION_PATH):
        fs.create_directory(fs.SIMU_VISUALIZATION_PATH)
    plt.savefig(f"{fs.SIMU_VISUALIZATION_PATH}{filename_prefix}_waiting_time_diff_with_n_{n0}_and_{n1}_rho_{rho}.png")

def visulize_all_parameters_pair_diff_waiting_time(n0, n1, miu, lambdas, fileName_prefix):
    i = 0
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    linestyles = ['-', '--', '-.', ':']
    markers = ['o', 's', 'D', 'v', '^', '<', '>', 'p', 'h', 'H', '8', '*', 'X']
    results = {}
    for lam in lambdas:
        # read from the file
        waiting_time_base = fs.read(n0, fs.SIMU_RESULT_PATH, lam, miu)[1]
        waiting_time_compared = fs.read(n1, fs.SIMU_RESULT_PATH, lam, miu)[1]
        rho = lam / miu
        # align the waiting times
        waiting_time_compared = waiting_time_compared[:len(waiting_time_base)]
        results[f"rho_{rho}"] = np.array(waiting_time_base) - np.array(waiting_time_compared)

    # align the waiting times in results
    min_len = min([len(value) for value in results.values()])
    for key, value in results.items():
        results[key] = value[:min_len]

    # plot the results
    plt.figure(figsize=(10, 6))
    plt.xlabel("Customer Number")
    plt.ylabel("Waiting Time Difference")
    plt.title(f"Difference in Waiting Time for Customers in Two Systems, with n={n0} and n={n1} servers")

    for key, value in results.items():
        plt.plot(value, label=key, color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])
        i += 1
    plt.legend()
    plt.grid()
    plt.savefig(f"{fs.SIMU_VISUALIZATION_PATH}{fileName_prefix}_waiting_time_diff_with_n_{n0}_and_{n1}.png")