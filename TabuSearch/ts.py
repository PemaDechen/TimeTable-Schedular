import random
from collections import deque
import copy

def tabu_search(initial_solution, cost_function, get_neighbors, tabu_size=10, max_iterations=100):
    current_solution = initial_solution
    current_cost = cost_function(current_solution)

    best_solution = copy.deepcopy(current_solution)
    best_cost = current_cost

    tabu_list = deque(maxlen=tabu_size)

    for iteration in range(max_iterations):
        neighbors = get_neighbors(current_solution)
        neighbors = [n for n in neighbors if n not in tabu_list]

        if not neighbors:
            print("No non-tabu neighbors left. Ending early.")
            break

        # Evaluate all neighbors
        evaluated = [(neighbor, cost_function(neighbor)) for neighbor in neighbors]
        evaluated.sort(key=lambda x: x[1])  # sort by cost

        next_solution, next_cost = evaluated[0]

        # Update best if improved
        if next_cost < best_cost:
            best_solution = copy.deepcopy(next_solution)
            best_cost = next_cost

        # Add current to tabu list
        tabu_list.append(current_solution)

        # Move to next
        current_solution = next_solution
        current_cost = next_cost

        print(f"Iteration {iteration}: Cost = {current_cost}, Best = {best_cost}")

    return best_solution, best_cost
