import pandas as pd

# Define the job data
jobs = [
    {'id': 'J1', 'size': 4, 'processing_time': 5, 'release_time': 10, 'due_date': 21, 'weight': 4},
    {'id': 'J2', 'size': 10, 'processing_time': 10, 'release_time': 10, 'due_date': 25, 'weight': 10},
    {'id': 'J3', 'size': 6, 'processing_time': 12, 'release_time': 15, 'due_date': 30, 'weight': 6},
    {'id': 'J4', 'size': 7, 'processing_time': 8, 'release_time': 28, 'due_date': 40, 'weight': 7},
    {'id': 'J5', 'size': 8, 'processing_time': 4, 'release_time': 30, 'due_date': 51, 'weight': 8},
    {'id': 'J6', 'size': 5, 'processing_time': 10, 'release_time': 31, 'due_date': 44, 'weight': 5},
    {'id': 'J7', 'size': 7, 'processing_time': 12, 'release_time': 33, 'due_date': 47, 'weight': 7},
    {'id': 'J8', 'size': 9, 'processing_time': 6, 'release_time': 35, 'due_date': 45, 'weight': 9},
    {'id': 'J9', 'size': 8, 'processing_time': 7, 'release_time': 40, 'due_date': 55, 'weight': 8},
    {'id': 'J10', 'size': 10, 'processing_time': 10, 'release_time': 43, 'due_date': 60, 'weight': 10},
]

# Machine capacity
BATCH_CAPACITY = 20

# Sort jobs by release time first, then by due date
jobs = sorted(jobs, key=lambda x: (x['release_time'], x['due_date']))

# Allocate jobs to batches
batches = []
current_batch = []
current_capacity = 0

for job in jobs:
    if current_capacity + job['size'] <= BATCH_CAPACITY:
        current_batch.append(job)
        current_capacity += job['size']
    else:
        batches.append(current_batch)
        current_batch = [job]
        current_capacity = job['size']

# Add the last batch
if current_batch:
    batches.append(current_batch)

# Calculate batch-wise information
batch_info = []
for batch_id, batch in enumerate(batches, start=1):
    release_time = max(job['release_time'] for job in batch)
    processing_time = max(job['processing_time'] for job in batch)
    completion_time = release_time + processing_time
    utilization = sum(job['size'] for job in batch)
    tardiness = sum(
        max(0, completion_time - job['due_date']) for job in batch
    )
    weighted_tardiness = sum(
        max(0, completion_time - job['due_date']) * job['weight'] for job in batch
    )
    batch_info.append({
        'Batch ID': batch_id,
        'Jobs': ', '.join(job['id'] for job in batch),
        'Processing Time': processing_time,
        'Release Time': release_time,
        'Completion Time': completion_time,
        'Utilization': utilization,
        'Tardiness': tardiness,
        'Weighted Tardiness': weighted_tardiness,
    })

# Create a pandas DataFrame
df = pd.DataFrame(batch_info)

# Display the table
print("\nBatch-wise Optimal Solution:")
print(df.to_string(index=False))
