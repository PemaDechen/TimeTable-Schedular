import math
import random
from intitial_solution import initial_solution
from parse_data import courses, rooms, weights, distributions, students
from sample_result import result
from cost_function import full_cost_function
from neighbor import generate_neighbor
from graph_utils import plot_cost_versus_iteration_graph

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
    current_cost, _ = full_cost_function(
        current_solution, courses, rooms, students, weights, distributions
    )
    best_solution = current_solution
    best_cost = current_cost
    temperature = initial_temp
    iteration = 0
    cost_history = []

    while temperature > min_temp and iteration < max_iterations:
        neighbor = generate_neighbor(current_solution, courses, rooms, weights)
        neighbor_cost, _ = full_cost_function(
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

        cost_history.append(current_cost)
        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_cost, cost_history


# Run SA
final_solution, final_cost, cost_history = simulated_annealing(
    initial_solution, courses, students, rooms, weights, distributions
)

plot_cost_versus_iteration_graph(cost_history)
result(final_solution, "SaResult")
