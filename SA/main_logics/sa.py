import math
import random
from intitial_solution import initial_solution
from parse_data import courses, rooms, weights, distributions, students
from sample_result import result
from cost_function import full_cost_function
from neighbor import generate_neighbor
from graph_utils import (
    plot_cost_versus_iteration_graph,
    plot_penalty_breakdown,
    save_in_text,
)
import time
import os
import csv


# Define Simulated Annealing Parameters
# initial_temp = 100
initial_temp = 10
cooling_rate = 0.95
min_temp = 1
max_iterations = 100


# Simulated Annealing main loop
def simulated_annealing(
    initial_solution, courses, students, rooms, weights, distributions
):
    current_solution = initial_solution
    current_cost, penalty_breakdown = full_cost_function(
        current_solution, courses, rooms, students, weights, distributions
    )
    best_solution = current_solution
    best_cost = current_cost
    best_penalty_breakdown = penalty_breakdown
    temperature = initial_temp
    iteration = 0
    cost_history = []

    while temperature > min_temp and iteration < max_iterations:
        print("It is running", temperature)
        neighbor = generate_neighbor(current_solution, courses, rooms, weights)
        neighbor_cost, neighbor_cost_penalty_breakdown = full_cost_function(
            neighbor, courses, rooms, students, weights, distributions
        )
        # Comparing the current_cost versus the neighbor_cost
        delta = neighbor_cost - current_cost

        if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
            current_solution = neighbor
            current_cost = neighbor_cost
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost
                best_penalty_breakdown = neighbor_cost_penalty_breakdown

        cost_history.append(current_cost)
        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_cost, cost_history, best_penalty_breakdown


# Create header if file doesn't exist yet
run_log_path = "./metrics_track/run_log.csv"
os.makedirs("./metrics_track", exist_ok=True)

# Preparing Excel for run_log.csv
if not os.path.exists(run_log_path):
    with open(run_log_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Run",
                "InitialTemp",
                "CoolingRate",
                "Iterations",
                "FinalCost",
                "ExecutionTime_sec",
                "StartTime",
                "EndTime",
            ]
        )

# Run SA
for i in range(1, 11):
    print(f"\n✨ Running SA Experiment {i} ✨")
    start_time = time.time()
    final_solution, final_cost, cost_history, best_penalty_breakdown = (
        simulated_annealing(
            initial_solution, courses, students, rooms, weights, distributions
        )
    )

    print("Graph Plotting Began")
    plot_cost_versus_iteration_graph(
        cost_history,
        "CostVSIteration" + str(i),
        "CostVSIteration" + str(initial_temp),
    )
    plot_penalty_breakdown(
        best_penalty_breakdown,
        "PenaltyBreakdown" + str(i),
        "PenaltyBreakDown" + str(initial_temp),
    )
    print("Graph  is saved")
    result(final_solution, "SaResult")
    os.makedirs("./metrics_track", exist_ok=True)

    # Endinggg
    print("Ending the time")
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"⏳ Execution Time: {execution_time:.4f} seconds")

    # Logging the log in excel
    with open(run_log_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                i,  # Run number
                initial_temp,
                cooling_rate,
                max_iterations,
                final_cost,
                round(execution_time, 4),
                start_time,
                end_time,
            ]
        )
