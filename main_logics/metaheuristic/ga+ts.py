# Re-execute necessary files after kernel reset
exec(open("/mnt/data/neighbor.py").read())
exec(open("/mnt/data/initial_solution.py").read())
exec(open("/mnt/data/cost_function.py").read())

# Redefine Hybrid GA + TS algorithm
import random
import copy
import hashlib
from collections import deque

def hash_solution(solution):
    return hashlib.md5(str(solution).encode()).hexdigest()

def hybrid_ga_ts(
    courses, rooms, students, weights, distributions,
    pop_size=30, generations=50, mutation_rate=0.2,
    tabu_size=50
):
    population = [generate_random_initial_solution(courses, rooms) for _ in range(pop_size)]
    best_solution = None
    best_cost = float('inf')
    cost_history = []

    def evaluate(sol):
        return full_cost_function(sol, courses, rooms, students, weights, distributions)[0]

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

    def mutate(solution, courses, rooms, weights):
        return generate_neighbor(solution, courses, rooms, weights)

    def tabu_search_local(solution, tabu_size=50, max_iterations=10):
        current = copy.deepcopy(solution)
        current_cost = evaluate(current)
        tabu_list = deque(maxlen=tabu_size)

        for _ in range(max_iterations):
            neighbors = []
            for _ in range(5):
                neighbor = generate_neighbor(current, courses, rooms, weights)
                if hash_solution(neighbor) not in tabu_list:
                    neighbors.append(neighbor)

            if not neighbors:
                break

            evaluated = [(n, evaluate(n)) for n in neighbors]
            evaluated.sort(key=lambda x: x[1])
            next_sol, next_cost = evaluated[0]

            current = next_sol
            current_cost = next_cost
            tabu_list.append(hash_solution(next_sol))

        return current, current_cost

    for gen in range(generations):
        evaluated = [(sol, evaluate(sol)) for sol in population]
        evaluated.sort(key=lambda x: x[1])

        if evaluated[0][1] < best_cost:
            best_solution = copy.deepcopy(evaluated[0][0])
            best_cost = evaluated[0][1]

        cost_history.append(best_cost)
        print(f"[Hybrid GA+TS] Generation {gen+1}: Best Cost = {best_cost}")

        next_gen = []
        while len(next_gen) < pop_size:
            parent1 = tournament_selection(evaluated)
            parent2 = tournament_selection(evaluated)
            child = crossover(parent1, parent2)
            next_gen.append(child)

        for i in range(len(next_gen)):
            if random.random() < mutation_rate:
                next_gen[i] = mutate(next_gen[i], courses, rooms, weights)

            next_gen[i], _ = tabu_search_local(next_gen[i], tabu_size=tabu_size)

        population = next_gen

    return best_solution, best_cost, cost_history

from parse_data import courses, rooms, students, weights, distributions

best_solution, best_cost, cost_history = hybrid_ga_ts(
    courses, rooms, students, weights, distributions,
    pop_size=30,
    generations=50,
    mutation_rate=0.2,
    tabu_size=50
)
