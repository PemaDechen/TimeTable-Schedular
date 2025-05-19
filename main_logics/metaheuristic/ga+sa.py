import random
import copy
import math
from index import generate_random_initial_solution, full_cost_function,generate_neighbor

def hybrid_ga_sa(
    courses, rooms, students, weights, distributions,
    pop_size=30, generations=50, mutation_rate=0.2,
    sa_temp=100, sa_cooling_rate=0.95, sa_min_temp=1
):
    # Initialize population
    population = [generate_random_initial_solution(courses, rooms) for _ in range(pop_size)]
    best_solution = None
    best_cost = float('inf')
    cost_history = []

    def evaluate(sol):
        return full_cost_function(sol, courses, rooms, students, weights, distributions)[0]

    def mutate(solution, courses, rooms, weights):
        """Apply a mutation using the same mutation logic as SA/TS."""
        return generate_neighbor(solution, courses, rooms, weights)

    def tournament_selection(evaluated, k=3):
        selected = random.sample(evaluated, k)
        selected.sort(key=lambda x: x[1])
        return copy.deepcopy(selected[0][0])

    def crossover(p1, p2):
        child = {}
        keys = list(p1.keys())
        split = random.randint(0, len(keys) - 1)
        for i, key in enumerate(keys):
            child[key] = p1[key] if i < split else p2[key]
        return child

    def simulated_annealing_local_search(solution, temp, cooling_rate, min_temp):
        current = copy.deepcopy(solution)
        current_cost = evaluate(current)

        while temp > min_temp:
            neighbor = generate_neighbor(current, courses, rooms, weights)
            neighbor_cost = evaluate(neighbor)

            if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temp):
                current = neighbor
                current_cost = neighbor_cost

            temp *= cooling_rate

        return current, current_cost

    for gen in range(generations):
        evaluated = [(sol, evaluate(sol)) for sol in population]
        evaluated.sort(key=lambda x: x[1])

        if evaluated[0][1] < best_cost:
            best_solution = copy.deepcopy(evaluated[0][0])
            best_cost = evaluated[0][1]

        cost_history.append(best_cost)
        print(f"[Hybrid GA+SA] Generation {gen+1}: Best Cost = {best_cost}")

        # Selection and crossover
        next_gen = []
        while len(next_gen) < pop_size:
            parent1 = tournament_selection(evaluated)
            parent2 = tournament_selection(evaluated)
            child = crossover(parent1, parent2)
            next_gen.append(child)

        # Mutation + Simulated Annealing refinement
        for i in range(len(next_gen)):
            if random.random() < mutation_rate:
                next_gen[i] = mutate(next_gen[i], courses, rooms, weights)

            # Apply local SA search to each individual
            next_gen[i], _ = simulated_annealing_local_search(next_gen[i], sa_temp, sa_cooling_rate, sa_min_temp)

        population = next_gen

    return best_solution, best_cost, cost_history

from parse_data import courses, rooms, students, weights, distributions

best_solution, best_cost, cost_history = hybrid_ga_sa(
    courses, rooms, students, weights, distributions,
    pop_size=30,
    generations=50,
    mutation_rate=0.2,
    sa_temp=100,
    sa_cooling_rate=0.95,
    sa_min_temp=1
)
