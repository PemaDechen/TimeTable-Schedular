import hashlib
from collections import deque
import copy
import random
from initial_solution import generate_random_initial_solution
from cost_function import full_cost_function
from parse_data import courses, rooms, students, weights, distributions
from neighbor import generate_neighbor


def hash_solution(solution):
    """Create a hash of the solution to use in tabu list."""
    return hashlib.md5(str(solution).encode()).hexdigest()

def tabu_search(tabu_size=50, max_iterations=500, neighbors_per_iteration=10):
    # Generate the initial solution
    current_solution = generate_random_initial_solution(courses, rooms)
    current_cost, _ = full_cost_function(
        current_solution, courses, rooms, students, weights, distributions
    )

    best_solution = copy.deepcopy(current_solution)
    best_cost = current_cost

    tabu_list = deque(maxlen=tabu_size)
    tabu_list.append(hash_solution(current_solution))

    cost_history = [current_cost]

    for iteration in range(max_iterations):
        neighbors = []

        for _ in range(neighbors_per_iteration):
            neighbor = generate_neighbor(current_solution, courses, rooms, weights)
            if hash_solution(neighbor) not in tabu_list:
                neighbors.append(neighbor)

        if not neighbors:
            print("No non-tabu neighbors available. Ending early.")
            break

        evaluated_neighbors = []
        for neighbor in neighbors:
            cost, _ = full_cost_function(
                neighbor, courses, rooms, students, weights, distributions
            )
            evaluated_neighbors.append((neighbor, cost))

        evaluated_neighbors.sort(key=lambda x: x[1])
        next_solution, next_cost = evaluated_neighbors[0]

        if next_cost < best_cost:
            best_solution = copy.deepcopy(next_solution)
            best_cost = next_cost

        tabu_list.append(hash_solution(next_solution))
        current_solution = next_solution
        current_cost = next_cost
        cost_history.append(current_cost)

        print(f"Iteration {iteration + 1}: Cost = {current_cost}, Best = {best_cost}")

    return best_solution, best_cost, cost_history


print(tabu_search())