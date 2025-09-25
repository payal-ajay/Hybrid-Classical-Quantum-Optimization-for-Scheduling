import numpy as np
from scipy.optimize import minimize

# -----------------------------
# Burn-in Scheduling: Total Weighted Tardiness (TWT)
# -----------------------------
def total_weighted_tardiness(schedule, processing_times, due_dates, weights):
    """
    Compute the Total Weighted Tardiness for a given schedule.

    Args:
        schedule (array): binary job schedule (0 = not scheduled, 1 = scheduled).
        processing_times (array): processing time for each job.
        due_dates (array): due date for each job.
        weights (array): weight (importance) of each job.

    Returns:
        float: total weighted tardiness.
    """
    time = 0
    twt = 0
    for i, job in enumerate(schedule):
        if job >= 0.5:  # treat >=0.5 as "job selected"
            time += processing_times[i]
            tardiness = max(0, time - due_dates[i])
            twt += weights[i] * tardiness
    return twt


# -----------------------------
# Simulation with Multiple Runs
# -----------------------------
def simulate_burnin(processing_times, due_dates, weights, num_runs=100, random_seed=None):
    """
    Optimize burn-in scheduling using COBYLA with multiple random restarts.

    Args:
        processing_times (array): processing time for each job.
        due_dates (array): due date for each job.
        weights (array): weight for each job.
        num_runs (int): number of optimization runs.
        random_seed (int | None): seed for reproducibility.

    Returns:
        best_schedule (array): best binary schedule found.
        best_twt (float): minimum total weighted tardiness.
    """
    rng = np.random.default_rng(seed=random_seed)
    n = len(processing_times)

    best_twt = np.inf
    best_schedule = None

    for run in range(num_runs):
        # 1. Random initialization (binary 0/1, converted to float for COBYLA)
        init_schedule = rng.integers(0, 2, size=n).astype(float)

        # 2. COBYLA optimization
        result = minimize(
            total_weighted_tardiness,
            init_schedule,
            args=(processing_times, due_dates, weights),
            method="COBYLA",
            options={"maxiter": 500, "disp": False}
        )

        # 3. Update best solution
        if result.fun < best_twt:
            best_twt = result.fun
            best_schedule = result.x

    # 4. Convert floating-point schedule → binary
    best_schedule_binary = np.round(best_schedule).astype(int)

    # 5. Output
    print("Optimal schedule:", best_schedule_binary)
    print("Minimum TWT found:", best_twt)

    return best_schedule_binary, best_twt


# -----------------------------
# Example Run
# -----------------------------
if __name__ == "__main__":
    # Example with 5 jobs
    processing_times = np.array([3, 2, 4, 1, 5])
    due_dates = np.array([4, 6, 7, 3, 10])
    weights = np.array([2, 1, 3, 2, 4])

    best_schedule, best_twt = simulate_burnin(
        processing_times, due_dates, weights,
        num_runs=100,
        random_seed=42
    )
