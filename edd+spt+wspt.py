import numpy as np
import pandas as pd
import os

# Define job data (same as original)
jobs = [
    {'id': 'J1', 'weight': 10, 'due_date': 21, 'processing_time': 5, 'release_time': 10},
    {'id': 'J2', 'weight': 8, 'due_date': 25, 'processing_time': 10, 'release_time': 15},
    {'id': 'J3', 'weight': 6, 'due_date': 30, 'processing_time': 12, 'release_time': 28},
    {'id': 'J4', 'weight': 7, 'due_date': 40, 'processing_time': 8, 'release_time': 31},
    {'id': 'J5', 'weight': 5, 'due_date': 51, 'processing_time': 4, 'release_time': 30},
    {'id': 'J6', 'weight': 9, 'due_date': 44, 'processing_time': 10, 'release_time': 31},
    {'id': 'J7', 'weight': 4, 'due_date': 47, 'processing_time': 12, 'release_time': 43},
    {'id': 'J8', 'weight': 3, 'due_date': 45, 'processing_time': 6, 'release_time': 35},
    {'id': 'J9', 'weight': 11, 'due_date': 55, 'processing_time': 7, 'release_time': 40},
    {'id': 'J10', 'weight': 2, 'due_date': 60, 'processing_time': 10, 'release_time': 43}
]

def create_batch_table(jobs, batches, approach_name):
    data = []
    twt = 0
    for batch_id, batch in enumerate(batches, start=1):
        completion_time = 0
        for job in batch:
            job_id = job['id']
            size = job['weight']
            due_date = job['due_date']
            processing_time = job['processing_time']
            release_time = job['release_time']

            # Calculate completion time and tardiness
            completion_time = max(completion_time, release_time) + processing_time
            tardiness = max(0, completion_time - due_date)
            weighted_tardiness = tardiness * size

            # Update TWT
            twt += weighted_tardiness

            # Append to data
            data.append([
                f"B{batch_id}", job_id, size, due_date, processing_time, release_time, completion_time, tardiness, weighted_tardiness
            ])

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'Batch ID', 'Job ID', 'Size', 'Due Date', 'Processing Time', 'Release Time', 'Completion Time', 'Tardiness', 'Weighted Tardiness'
    ])
    
    # Add total row
    total_row = pd.DataFrame([['Total', '', '', '', '', '', '', '', twt]], 
                              columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)

    print(f"\n{approach_name} Approach TWT: {twt}\n")
    print(df)
    return df

# EDD Scheduling (Earliest Due Date)
def edd_scheduling(jobs):
    # Sort jobs by due date
    sorted_jobs = sorted(jobs, key=lambda x: x['due_date'])
    
    # Create batches with jobs close in due dates
    batches = []
    current_batch = []
    current_due_date = sorted_jobs[0]['due_date']

    for job in sorted_jobs:
        if abs(job['due_date'] - current_due_date) <= 15:
            current_batch.append(job)
        else:
            batches.append(current_batch)
            current_batch = [job]
            current_due_date = job['due_date']

    if current_batch:
        batches.append(current_batch)

    return batches

# SPT Scheduling (Shortest Processing Time)
def spt_scheduling(jobs):
    # Sort jobs by processing time
    sorted_jobs = sorted(jobs, key=lambda x: x['processing_time'])
    
    # Create batches with jobs close in processing times
    batches = []
    current_batch = []
    current_processing_time = sorted_jobs[0]['processing_time']

    for job in sorted_jobs:
        if abs(job['processing_time'] - current_processing_time) <= 5:
            current_batch.append(job)
        else:
            batches.append(current_batch)
            current_batch = [job]
            current_processing_time = job['processing_time']

    if current_batch:
        batches.append(current_batch)

    return batches

# WSPT Scheduling (Weighted Shortest Processing Time)
def wspt_scheduling(jobs):
    # Sort jobs by weight/processing time ratio
    sorted_jobs = sorted(jobs, key=lambda x: x['weight'] / x['processing_time'], reverse=True)
    
    # Create batches with jobs close in WSPT ratios
    batches = []
    current_batch = []
    current_wspt_ratio = sorted_jobs[0]['weight'] / sorted_jobs[0]['processing_time']

    for job in sorted_jobs:
        wspt_ratio = job['weight'] / job['processing_time']
        if abs(wspt_ratio - current_wspt_ratio) <= 1:
            current_batch.append(job)
        else:
            batches.append(current_batch)
            current_batch = [job]
            current_wspt_ratio = wspt_ratio

    if current_batch:
        batches.append(current_batch)

    return batches

# Hybrid Scheduling Approach
def hybrid_scheduling(jobs):
    # Combine multiple scheduling strategies
    edd_batches = edd_scheduling(jobs)
    spt_batches = spt_scheduling(jobs)
    wspt_batches = wspt_scheduling(jobs)
    
    # Merge and optimize batches
    hybrid_batches = []
    
    # Combine all batches
    all_jobs = [job for batch in (edd_batches + spt_batches + wspt_batches) for job in batch]
    
    # Sort combined jobs by a composite score
    sorted_jobs = sorted(all_jobs, key=lambda x: (
        x['due_date'],                 # Primary: Due date
        x['weight'] / x['processing_time'],  # Secondary: WSPT ratio
        x['processing_time']            # Tertiary: Processing time
    ))
    
    # Create new batches with optimized sorting
    current_batch = []
    current_due_date = sorted_jobs[0]['due_date']

    for job in sorted_jobs:
        if (not current_batch or 
            (abs(job['due_date'] - current_due_date) <= 20 and 
             len(current_batch) < 4)):  # Limit batch size
            current_batch.append(job)
        else:
            hybrid_batches.append(current_batch)
            current_batch = [job]
            current_due_date = job['due_date']

    if current_batch:
        hybrid_batches.append(current_batch)

    return hybrid_batches

# Ensure output directory exists
output_dir = 'scheduler_results'
os.makedirs(output_dir, exist_ok=True)

# Execute and compare different scheduling approaches
edd_batches = edd_scheduling(jobs)
edd_df = create_batch_table(jobs, edd_batches, "EDD Scheduling")

spt_batches = spt_scheduling(jobs)
spt_df = create_batch_table(jobs, spt_batches, "SPT Scheduling")

wspt_batches = wspt_scheduling(jobs)
wspt_df = create_batch_table(jobs, wspt_batches, "WSPT Scheduling")

hybrid_batches = hybrid_scheduling(jobs)
hybrid_df = create_batch_table(jobs, hybrid_batches, "Hybrid Scheduling")

# Save results to CSV with unique filenames
try:
    edd_df.to_csv(os.path.join(output_dir, 'scheduler_edd_results.csv'), index=False)
    spt_df.to_csv(os.path.join(output_dir, 'scheduler_spt_results.csv'), index=False)
    wspt_df.to_csv(os.path.join(output_dir, 'scheduler_wspt_results.csv'), index=False)
    hybrid_df.to_csv(os.path.join(output_dir, 'scheduler_hybrid_results.csv'), index=False)
    print("Results saved to CSV in 'scheduler_results' directory.")
except Exception as e:
    print(f"An error occurred while saving CSV files: {e}")