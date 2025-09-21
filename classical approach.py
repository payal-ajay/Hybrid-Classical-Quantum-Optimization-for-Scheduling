import random
import math
# Step 1: Problem Initialization
num_jobs = 25  # Number of jobs (Example for N=25)
batch_capacity = 50  # Example batch capacity
release_times = [random.randint(1, 20) for _ in range(num_jobs)]  # Ranges from Table 6
processing_times = [random.randint(1, 10) for _ in range(num_jobs)]
due_dates = [release_times[i] + processing_times[i] + random.randint(1, 30) for i in range(num_jobs)]
job_sizes = [random.randint(4, 10) for _ in range(num_jobs)]

# Step 2: Heuristic Scheduling
def schedule_jobs():
    """Schedules jobs using a simple dispatching heuristic (EDD)."""
    jobs = list(range(num_jobs))
    sorted_jobs = sorted(jobs, key=lambda x: due_dates[x])  # Earliest Due Date (EDD) heuristic
    schedule = []
    current_batch = []
    current_capacity = 0

    for job in sorted_jobs:
        if current_capacity + job_sizes[job] <= batch_capacity:
            current_batch.append(job)
            current_capacity += job_sizes[job]
        else:
            schedule.append(current_batch)
            current_batch = [job]
            current_capacity = job_sizes[job]

    if current_batch:
        schedule.append(current_batch)

    return schedule

# Step 3: Calculate Total Weighted Tardiness (TWT)
def calculate_twt(schedule):
    """Calculate Total Weighted Tardiness (TWT)."""
    total_twt = 0
    for batch in schedule:
        completion_time = max(due_dates[job] for job in batch)
        for job in batch:
            tardiness = max(0, completion_time - due_dates[job])
            total_twt += job_sizes[job] * tardiness
    return total_twt

# Run the scheduler and display results
schedule = schedule_jobs()
twt = calculate_twt(schedule)
print("Job Schedule (Batch-wise):", schedule)
print("Total Weighted Tardiness (TWT):", twt)
