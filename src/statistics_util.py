import file_sys as fs
import numpy as np
import scipy.stats as stats
import visualize_util as vu

# 
def calculate_pair_confidence_intervals(n0, n1, lam, mu, CI=0.95):
    """
    Calculate confidence intervals for the difference in means of two samples

    Parameters:
    ----------
    n0: int
        number of servers in the first system
    n1: int
        number of servers in the second system
    lam: float
        arrival rate
    mu: float
        service rate

    Returns:
    ----------
    dict
        A dictionary containing the following keys:
            - lower_bound: float
                lower bound of the confidence interval
            - upper_bound: float
                upper bound of the confidence interval
            - hypothesis_mean: float
                mean of the hypothesis
            - included_in_CI: bool
                True if the hypothesis mean is included in the confidence interval
            - standard_deviation: float
                standard deviation of the difference in means
    """
    _, _, waiting_times_base, _ = fs.read(n0, fs.SIMU_RESULT_PATH, lam, mu)
    _, _, waiting_times_compared, _ = fs.read(n1, fs.SIMU_RESULT_PATH, lam, mu)

    confidence_level = CI
    lamb_CI = stats.norm.ppf((1 + confidence_level) / 2) # for 95% it should be 1.96

    # Truncate the waiting_times_compared to the length of waiting_times_base
    waiting_times_compared = waiting_times_compared[:len(waiting_times_base)]
    print(f"len(waiting_times_base): {len(waiting_times_base)}")
    RV_diff_waiting_times = np.array(waiting_times_base) - np.array(waiting_times_compared)

    # Calculate the mean of the difference in waiting times
    RVs_mean_diff = np.mean(RV_diff_waiting_times)
    RVs_std = np.std(RV_diff_waiting_times, ddof=1) 
    RVs_std_error = RVs_std / np.sqrt(len(RV_diff_waiting_times))
    upper_bound = RVs_mean_diff + lamb_CI * RVs_std_error
    lower_bound = RVs_mean_diff - lamb_CI * RVs_std_error

    # Instead of Z value, we here use upper and lower bounds to check if the mean is within the confidence interval
    # we expecect the mean to be 0, so we check if the mean is within the confidence interval
    included_in_CI = lower_bound <= 0 <= upper_bound
    vu.plot_pair_waiting_time_diff(n0, n1, lam / mu, RV_diff_waiting_times, "multiSys")

    return {
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'hypothesis_mean': 0,
        'included_in_CI': included_in_CI,
        'standard_deviation': RVs_std
    }

if __name__ == "__main__":
    n0 = 1
    n1 = 2
    lam = 0.5
    miu = 1.0
    result = calculate_pair_confidence_intervals(n0, n1, lam, miu)
    print(result)