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

# Define Simulated Annealing Parameters
# initial_temp = 1000
initial_temp = 10
cooling_rate = 0.95
min_temp = 1
# max_iterations = 1000
max_iterations = 10


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


# Run SA
start_time = time.time()
final_solution, final_cost, cost_history, best_penalty_breakdown = simulated_annealing(
    initial_solution, courses, students, rooms, weights, distributions
)

# plot_cost_versus_iteration_graph(cost_history)
# plot_penalty_breakdown(best_penalty_breakdown, filename="penalty_breakdown.png")
result(final_solution, "SaResult")
end_time = time.time()
execution_time = end_time - start_time
print(f"⏳ Execution Time: {execution_time:.4f} seconds")
save_in_text("Execution.txt", [start_time, end_time, execution_time])
