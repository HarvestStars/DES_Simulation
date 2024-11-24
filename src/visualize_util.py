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
        _, _, waiting_time_base, _ = fs.read(n0, fs.SIMU_RESULT_PATH, lam, miu)
        _, _, waiting_time_compared, _ = fs.read(n1, fs.SIMU_RESULT_PATH, lam, miu)
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

def visulize_all_parameters_pair_diff_waiting_time_sjf(miu, lambdas, fileName_prefix):
    i = 0
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    linestyles = ['-', '--', '-.', ':']
    markers = ['o', 's', 'D', 'v', '^', '<', '>', 'p', 'h', 'H', '8', '*', 'X']
    results = {}
    # plot the results
    plt.figure(figsize=(10, 6))
    plt.xlabel("Customer Number")
    plt.ylabel("Waiting Time Difference")
    plt.title(f"Difference in Waiting Time for Customers in SFJ and FIFO Systems, with n=1 servers")
    for lam in lambdas:
        # read from the file
        customers_base, _, waiting_time_base, _= fs.read(1, fs.SIMU_RESULT_PATH, lam, miu, prefix="Comparison_FIFO")
        customers_compared, _, waiting_time_compared, _ = fs.read(1, fs.SIMU_RESULT_PATH, lam, miu, prefix="Comparison_SJF")
        # reorder the waiting_time_compared based on the customer number
        sorted_data = sorted(zip(customers_compared, waiting_time_compared), key=lambda x: x[0])
        customers_compared, waiting_time_compared = zip(*sorted_data)
        customers_compared = list(customers_compared)
        waiting_time_compared = list(waiting_time_compared)

        rho = lam / miu
        plt.plot(customers_base, waiting_time_base, label=f"FIFO_rho_{rho}", color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])
        i += 1
        plt.plot(customers_compared, waiting_time_compared, label=f"SJF_rho_{rho}", color=colors[i % len(colors)], linestyle=linestyles[i % len(linestyles)])
        
        # # reorder the waiting_time_compared based on the customer number
        # # attention: the customer number in the two systems may not be the same
        # # so we should compare the customers in both systems and pick up the overlap part, if customer is not in both, then remove it from the existed system
        # customers_base_set = set(customers_base)
        # customers_compared_set = set(customers_compared)
        # customers_overlap = customers_base_set & customers_compared_set
        # customers_base = [customer for customer in customers_base if customer in customers_overlap]
        # waiting_time_base = [waiting_time_base[customers_base.index(customer)] for customer in customers_overlap]
        # customers_compared = [customer for customer in customers_compared if customer in customers_overlap]
        # waiting_time_compared = [waiting_time_compared[customers_compared.index(customer)] for customer in customers_overlap]
        
        # # after that, we reorder the waiting_time_compared based on the customer number in the base system
        # waiting_time_compared = [waiting_time_compared[customers_compared.index(customer)] for customer in customers_base]
        # results[f"rho_{rho}"] = np.array(waiting_time_base) - np.array(waiting_time_compared)

    # # align the waiting times in results
    # min_len = min([len(value) for value in results.values()])
    # for key, value in results.items():
    #     results[key] = value[:min_len]

    plt.legend()
    plt.grid()
    plt.savefig(f"{fs.SIMU_VISUALIZATION_PATH}{fileName_prefix}_waiting_time_diff_with_n_1.png")

# Example Usage:
if __name__ == "__main__":
    visulize_all_parameters_pair_diff_waiting_time_sjf(1.0, [0.9], "SJF")