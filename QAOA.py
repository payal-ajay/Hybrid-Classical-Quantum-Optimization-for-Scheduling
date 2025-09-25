import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import Sampler, Estimator
from qiskit.quantum_info import Pauli
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.converters import QuadraticProgramToQubo

# -----------------------------
# 1. Burn-in Scheduling → QUBO Formulation
# -----------------------------
def build_burnin_qubo(processing_times, due_dates, weights):
    """
    Build a QUBO for the burn-in scheduling problem:
    Objective: Minimize Total Weighted Tardiness (TWT).
    
    Args:
        processing_times (list[int]): processing time of each job
        due_dates (list[int]): due date of each job
        weights (list[int]): job weights

    Returns:
        QuadraticProgram: optimization problem
    """
    n = len(processing_times)
    qp = QuadraticProgram()

    # Binary variables: x_i = 1 if job i is selected, else 0
    for i in range(n):
        qp.binary_var(f"x_{i}")

    # Objective: Σ w_i * max(0, C_i - d_i)
    # Simplified linear penalty: sum(weights[i] * (processing_times[i] - due_dates[i]) * x_i)
    # (For demonstration – real tardiness encoding may require auxiliary vars)
    linear = {}
    for i in range(n):
        linear[f"x_{i}"] = weights[i] * (processing_times[i] - due_dates[i])

    qp.minimize(linear=linear)

    return qp


# -----------------------------
# 2. Solve with QAOA
# -----------------------------
def simulate_burnin_qaoa(processing_times, due_dates, weights, p=1, shots=1024):
    """
    Solve the burn-in scheduling problem using QAOA.

    Args:
        processing_times (list[int])
        due_dates (list[int])
        weights (list[int])
        p (int): QAOA depth (number of alternating layers)
        shots (int): number of measurement shots

    Returns:
        best_schedule (list[int]): best binary schedule found
        best_obj (float): objective value (TWT approx)
    """
    # 1. Build QUBO
    qp = build_burnin_qubo(processing_times, due_dates, weights)

    # 2. Convert to QUBO form
    conv = QuadraticProgramToQubo()
    qubo = conv.convert(qp)

    # 3. Setup QAOA with COBYLA optimizer
    optimizer = COBYLA(maxiter=200)
    qaoa = QAOA(optimizer=optimizer, reps=p, sampler=Sampler())

    # 4. Solve with QAOA
    result = qaoa.compute_minimum_eigenvalue(qubo.to_ising()[0])
    
    # 5. Extract solution
    samples = result.samples
    best_sample = max(samples, key=lambda s: s.probability)
    best_schedule = [int(b) for b in best_sample.x]
    best_obj = qp.objective.evaluate(best_schedule)

    print("Best schedule found (QAOA):", best_schedule)
    print("Approximate minimum TWT:", best_obj)

    return best_schedule, best_obj


# -----------------------------
# Example Run
# -----------------------------
if __name__ == "__main__":
    # Example jobs
    processing_times = [3, 2, 4, 1]
    due_dates = [4, 6, 7, 3]
    weights = [2, 1, 3, 2]

    best_schedule, best_obj = simulate_burnin_qaoa(processing_times, due_dates, weights, p=1)
