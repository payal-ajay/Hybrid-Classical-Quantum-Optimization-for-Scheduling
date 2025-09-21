import numpy as np
import pandas as pd
import os
from typing import List, Dict, Any

# Define job data
jobs = [
    {'id': 'J1', 'weight': 1, 'due_date': 50, 'processing_time': 16, 'release_time': 30, 'energy_consumption': 6},
    {'id': 'J2', 'weight': 9, 'due_date': 30, 'processing_time': 13, 'release_time': 25, 'energy_consumption': 3},
    {'id': 'J3', 'weight': 4, 'due_date': 45, 'processing_time': 11, 'release_time': 58, 'energy_consumption': 4},
    {'id': 'J4', 'weight': 3, 'due_date': 60, 'processing_time': 3, 'release_time': 34, 'energy_consumption': 4},
    {'id': 'J5', 'weight': 1, 'due_date': 21, 'processing_time': 14, 'release_time': 20, 'energy_consumption': 12},
    {'id': 'J6', 'weight': 10, 'due_date': 34, 'processing_time': 20, 'release_time': 21, 'energy_consumption': 6},
    {'id': 'J7', 'weight': 6, 'due_date': 46, 'processing_time': 15, 'release_time': 50, 'energy_consumption': 25},
    {'id': 'J8', 'weight': 7, 'due_date': 33, 'processing_time': 12, 'release_time': 31, 'energy_consumption': 13},
    {'id': 'J9', 'weight': 11, 'due_date': 65, 'processing_time': 5, 'release_time': 42, 'energy_consumption': 24},
    {'id': 'J10', 'weight': 3, 'due_date': 10, 'processing_time': 20, 'release_time': 22, 'energy_consumption': 15}
]

def create_batch_table(jobs, batches, approach_name):
    data = []
    twt = 0
    for batch_id, batch in enumerate(batches, start=1):
        # Batch-level metrics
        batch_release_time = min(job['release_time'] for job in batch)
        batch_processing_time = max(job['processing_time'] for job in batch)
        batch_due_date = min(job['due_date'] for job in batch)
        
        # Calculate completion time and tardiness at batch level
        completion_time = batch_release_time + batch_processing_time
        tardiness = max(0, completion_time - batch_due_date)
        
        # Calculate batch-level weighted tardiness
        batch_weight = sum(job['weight'] for job in batch)
        weighted_tardiness = tardiness * batch_weight

        twt += weighted_tardiness

        # Add job details to data
        for job in batch:
            data.append([
                f"B{batch_id}", job['id'], job['weight'], job['due_date'], 
                job['processing_time'], job['release_time'], 
                completion_time, tardiness, weighted_tardiness
            ])

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'Batch ID', 'Job ID', 'Size', 'Due Date', 
        'Processing Time', 'Release Time', 
        'Batch Completion Time', 'Batch Tardiness', 'Weighted Tardiness'
    ])
    
    # Add total row
    total_row = pd.DataFrame([['Total', '', '', '', '', '', '', '', twt]], 
                              columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)

    print(f"\n{approach_name} Approach TWT: {twt}\n")
    print(df)
    return df

def create_batches(jobs, max_batch_size: int = 4, min_batch_size: int = 2):
    """
    Generic batch formation function that can work with different sorting criteria
    
    Args:
        jobs (List[Dict]): List of jobs to be batched
        max_batch_size (int): Maximum number of jobs in a batch
        min_batch_size (int): Minimum number of jobs in a batch
    
    Returns:
        List[List[Dict]]: Batches of jobs
    """
    # Batch formation
    batches = []
    current_batch = []
    
    for job in jobs:
        # If current batch is at max size, start a new batch
        if len(current_batch) >= max_batch_size:
            batches.append(current_batch)
            current_batch = []
        
        current_batch.append(job)
    
    # Add the last batch if it's not empty
    if current_batch:
        # If last batch is too small, try to merge with previous batch
        if len(current_batch) < min_batch_size and batches:
            batches[-1].extend(current_batch)
        else:
            batches.append(current_batch)
    
    # Ensure each batch meets minimum size requirement
    final_batches = []
    current_merge_batch = []
    
    for batch in batches:
        current_merge_batch.extend(batch)
        
        # If current merged batch exceeds max size, split it
        while len(current_merge_batch) > max_batch_size:
            final_batches.append(current_merge_batch[:max_batch_size])
            current_merge_batch = current_merge_batch[max_batch_size:]
        
        # If merged batch meets minimum size, add it
        if len(current_merge_batch) >= min_batch_size:
            final_batches.append(current_merge_batch)
            current_merge_batch = []
    
    # Handle any remaining jobs
    if current_merge_batch:
        final_batches.append(current_merge_batch)
    
    return final_batches

def edd_scheduling(jobs):
    # Classical Earliest Due Date (EDD) scheduling
    # First, sort by due date
    sorted_jobs = sorted(jobs, key=lambda x: x['due_date'])
    
    # Then create batches
    return create_batches(sorted_jobs)

def advanced_hybrid_scheduling(jobs, max_batch_size: int = 4, min_batch_size: int = 2):
    # Normalize job parameters
    params = ['energy_consumption', 'processing_time', 'weight', 'due_date']
    
    for param in params:
        values = [job[param] for job in jobs]
        min_val, max_val = min(values), max(values)
        
        # Avoid division by zero
        if min_val == max_val:
            continue
        
        for job in jobs:
            job[f'normalized_{param}'] = (job[param] - min_val) / (max_val - min_val)
    
    # Calculate Job Priority Index (JPI)
    def calculate_jpi(job):
        # Slack time calculation
        slack_time = job['due_date'] - job['release_time'] - job['processing_time']
        
        # Advanced JPI calculation with batch-level considerations
        jpi = (
            -2 * slack_time +  # Slack time penalty
            5 * job['normalized_energy_consumption'] +  # Energy efficiency
            3 * job['normalized_processing_time'] +  # Processing efficiency
            4 * job['normalized_weight'] +  # Job importance
            2 * job['normalized_due_date']  # Time criticality
        )
        
        return jpi
    
    # Calculate JPI for each job
    for job in jobs:
        job['jpi'] = calculate_jpi(job)
    
    # Sort jobs by JPI
    sorted_jobs = sorted(jobs, key=lambda x: x['jpi'])
    
    # Create batches
    return create_batches(sorted_jobs, max_batch_size, min_batch_size)

# Ensure output directory exists
output_dir = 'scheduling_optimization'
os.makedirs(output_dir, exist_ok=True)

# Execute and compare scheduling approaches
edd_results = edd_scheduling(jobs)
edd_df = create_batch_table(jobs, edd_results, "EDD Batch Scheduling")

hybrid_results = advanced_hybrid_scheduling(jobs)
hybrid_df = create_batch_table(jobs, hybrid_results, "Advanced Hybrid Scheduling")

# Save results to CSV
try:
    edd_df.to_csv(os.path.join(output_dir, 'edd_batch_results.csv'), index=False)
    hybrid_df.to_csv(os.path.join(output_dir, 'advanced_hybrid_results.csv'), index=False)
    print("Results saved to CSV in 'scheduling_optimization' directory.")
except Exception as e:
    print(f"An error occurred while saving CSV files: {e}")

# Print batch details
print("\nEDD Batch Composition:")
for i, batch in enumerate(edd_results, 1):
    print(f"Batch {i}: {[job['id'] for job in batch]} (Size: {len(batch)})")
    print(f"  Batch Release Time: {min(job['release_time'] for job in batch)}")
    print(f"  Batch Processing Time: {max(job['processing_time'] for job in batch)}")
    print(f"  Batch Due Date: {min(job['due_date'] for job in batch)}")

print("\nAdvanced Hybrid Batch Composition:")
for i, batch in enumerate(hybrid_results, 1):
    print(f"Batch {i}: {[job['id'] for job in batch]} (Size: {len(batch)})")
    print(f"  Batch Release Time: {min(job['release_time'] for job in batch)}")
    print(f"  Batch Processing Time: {max(job['processing_time'] for job in batch)}")
    print(f"  Batch Due Date: {min(job['due_date'] for job in batch)}")



