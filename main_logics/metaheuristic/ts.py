import os
import hashlib
import copy
import random
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from datetime import datetime
from collections import deque
import multiprocessing

from index import (
    plot_cost_versus_iteration_graph,
    plot_penalty_breakdown,
    result,
    generate_neighbor,
    courses,
    rooms,
    students,
    weights,
    distributions,
    generate_random_initial_solution,
    full_cost_function,
)


def hash_solution(solution):
    return hashlib.md5(str(solution).encode()).hexdigest()


def tabu_search(
    tabu_size=50,
    max_iterations=500,
    neighbors_per_iteration=10,
    enable_output=True,
    label="TabuSearch_FinalResult",
):
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

        evaluated_neighbors = [
            (
                n,
                full_cost_function(n, courses, rooms, students, weights, distributions)[
                    0
                ],
            )
            for n in neighbors
        ]
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

    if enable_output:
        plot_cost_versus_iteration_graph(
            cost_history, title=f"TS: Cost vs Iteration ({label})"
        )

        final_cost, _, penalty_breakdown = full_cost_function(
            best_solution, courses, rooms, students, weights, distributions
        )
        plot_penalty_breakdown(
            penalty_breakdown, title=f"TS: Penalty Breakdown ({label})"
        )

        result(best_solution, label)

    return best_solution, best_cost, cost_history

def ts_worker(run_id, tabu_size):
    sol, cost, history = tabu_search(tabu_size=tabu_size, enable_output=False)
    final_cost, penalty = full_cost_function(
        sol, courses, rooms, students, weights, distributions
    )
    return {
        "Run": run_id,
        "Tabu Size": tabu_size,
        "Best Cost": final_cost,
        "Room Penalty": penalty.get("room", 0),
        "Student Penalty": penalty.get("student", 0),
        "Distribution Penalty": penalty.get("distribution", 0),
    }

def run_parallel_ts_experiments():
 
    configs = [(i, t) for t in [10, 50, 100] for i in range(1, 6)]
    with multiprocessing.Pool(
        processes=min(multiprocessing.cpu_count(), len(configs))
    ) as pool:
        results = pool.starmap(ts_worker, configs)

    df = pd.DataFrame(results)
    os.makedirs("output_files/metrics_track", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(
        f"output_files/metrics_track/tabu_experiment_{timestamp}.csv", index=False
    )

    plt.figure(figsize=(8, 5))
    sns.boxplot(x="Tabu Size", y="Best Cost", data=df)
    plt.title("Tabu Search: Best Cost vs Tabu Size")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return df


