import os
import random
import copy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from initial_solution import generate_random_initial_solution
from cost_function import full_cost_function
from parse_data import courses, rooms, students, weights, distributions
from neighbor import generate_neighbor
from final_result import result
from graph_utils_patched import plot_cost_versus_iteration_graph, plot_penalty_breakdown
import hashlib
from collections import deque
import math

def initialize_population(pop_size):
    return [generate_random_initial_solution(courses, rooms) for _ in range(pop_size)]

def evaluate_population(population):
    return [(individual, full_cost_function(individual, courses, rooms, students, weights, distributions)[0])
            for individual in population]

def tournament_selection(evaluated_pop, tournament_size=3):
    selected = random.sample(evaluated_pop, tournament_size)
    selected.sort(key=lambda x: x[1])
    return copy.deepcopy(selected[0][0])

def crossover(parent1, parent2):
    child = {}
    keys = list(parent1.keys())
    split = random.randint(0, len(keys) - 1)
    for i, key in enumerate(keys):
        child[key] = parent1[key] if i < split else parent2[key]
    return child

def mutate(solution):
    return generate_neighbor(solution, courses, rooms, weights)

def hash_solution(solution):
    return hashlib.md5(str(solution).encode()).hexdigest()

def simulated_annealing_local(solution, temp=100, cooling_rate=0.95, min_temp=1):
    current = copy.deepcopy(solution)
    current_cost = full_cost_function(current, courses, rooms, students, weights, distributions)[0]

    while temp > min_temp:
        neighbor = generate_neighbor(current, courses, rooms, weights)
        neighbor_cost = full_cost_function(neighbor, courses, rooms, students, weights, distributions)[0]

        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
            current = neighbor
            current_cost = neighbor_cost

        temp *= cooling_rate

    return current, current_cost

def hybrid_sa_ts(pop_size=30, generations=50, mutation_rate=0.2, sa_temp=100, sa_cooling_rate=0.95, sa_min_temp=1, tabu_size=50, enable_output=True, label="HybridSA_TS_FinalResult"):
    population = initialize_population(pop_size)
    best_solution = None
    best_cost = float('inf')
    cost_history = []

    for gen in range(generations):
        evaluated = evaluate_population(population)
        evaluated.sort(key=lambda x: x[1])

        if evaluated[0][1] < best_cost:
            best_solution = evaluated[0][0]
            best_cost = evaluated[0][1]

        cost_history.append(best_cost)
        print(f"[Hybrid SA+TS] Generation {gen+1}: Best Cost = {best_cost}")

        next_gen = []
        while len(next_gen) < pop_size:
            parent1 = tournament_selection(evaluated)
            parent2 = tournament_selection(evaluated)
            child = crossover(parent1, parent2)
            next_gen.append(child)

        for i in range(len(next_gen)):
            if random.random() < mutation_rate:
                next_gen[i] = mutate(next_gen[i])

            # Apply Simulated Annealing
            next_gen[i], _ = simulated_annealing_local(next_gen[i], temp=sa_temp, cooling_rate=sa_cooling_rate, min_temp=sa_min_temp)

            # Then apply Tabu Search on result
            next_gen[i], _ = tabu_search_local(next_gen[i], tabu_size=tabu_size)

        population = next_gen

    if enable_output:
        plot_cost_versus_iteration_graph(cost_history, title=f"Hybrid SA+TS: Cost vs Generation ({label})")
        final_cost, _, penalty_breakdown = full_cost_function(best_solution, courses, rooms, students, weights, distributions)
        plot_penalty_breakdown(penalty_breakdown, title=f"Hybrid SA+TS: Penalty Breakdown ({label})")
        result(best_solution, label)

    return best_solution, best_cost, cost_history

def sa_ts_worker(run_id, pop_size):
    sol, cost, history = hybrid_sa_ts(pop_size=pop_size, enable_output=False)
    final_cost, _, penalty = full_cost_function(sol, courses, rooms, students, weights, distributions)
    return {
        "Run": run_id,
        "Population Size": pop_size,
        "Best Cost": final_cost,
        "Room Penalty": penalty.get("room", 0),
        "Student Penalty": penalty.get("student", 0),
        "Distribution Penalty": penalty.get("distribution", 0),
    }

def run_parallel_hybrid_sa_ts_experiments():
    import multiprocessing
    configs = [(i, p) for p in [20, 30, 50] for i in range(1, 6)]

    with multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(configs))) as pool:
        results = pool.starmap(sa_ts_worker, configs)

    df = pd.DataFrame(results)
    os.makedirs("output_files/metrics_track", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"output_files/metrics_track/hybrid_sa_ts_experiment_{timestamp}.csv", index=False)

    plt.figure(figsize=(8, 5))
    sns.boxplot(x='Population Size', y='Best Cost', data=df)
    plt.title("Hybrid SA+TS: Best Cost vs Population Size")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return df

    
