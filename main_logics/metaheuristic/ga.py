# Load all required modules after re-upload
exec(open("/mnt/data/neighbor.py").read())
exec(open("/mnt/data/initial_solution.py").read())
exec(open("/mnt/data/cost_function.py").read())

# Redefine the Genetic Algorithm implementation using the reloaded modules
import random
import copy

def initialize_population(pop_size, courses, rooms):
    """Initialize a population of random solutions."""
    return [generate_random_initial_solution(courses, rooms) for _ in range(pop_size)]

def evaluate_population(population, courses, rooms, students, weights, distributions):
    """Evaluate all individuals and return (solution, cost) tuples."""
    return [(individual, full_cost_function(individual, courses, rooms, students, weights, distributions)[0])
            for individual in population]

def tournament_selection(evaluated_pop, tournament_size=3):
    """Select an individual via tournament selection."""
    selected = random.sample(evaluated_pop, tournament_size)
    selected.sort(key=lambda x: x[1])
    return copy.deepcopy(selected[0][0])  # return solution part

def crossover(parent1, parent2):
    """Simple one-point crossover for timetable dictionaries."""
    child = {}
    keys = list(parent1.keys())
    split = random.randint(0, len(keys) - 1)
    for i, key in enumerate(keys):
        child[key] = parent1[key] if i < split else parent2[key]
    return child

def mutate(solution, courses, rooms, weights):
    """Apply a mutation using the same mutation logic as SA/TS."""
    return generate_neighbor(solution, courses, rooms, weights)

def genetic_algorithm(
    courses, rooms, students, weights, distributions,
    pop_size=30, generations=100, mutation_rate=0.2
):
    # Step 1: Initialize
    population = initialize_population(pop_size, courses, rooms)

    best_solution = None
    best_cost = float('inf')
    cost_history = []

    for gen in range(generations):
        evaluated = evaluate_population(population, courses, rooms, students, weights, distributions)
        evaluated.sort(key=lambda x: x[1])  # Sort by cost

        # Track best
        if evaluated[0][1] < best_cost:
            best_solution = evaluated[0][0]
            best_cost = evaluated[0][1]

        cost_history.append(best_cost)
        print(f"Generation {gen+1}: Best Cost = {best_cost}")

        # Step 2: Selection + Crossover
        next_gen = []
        while len(next_gen) < pop_size:
            parent1 = tournament_selection(evaluated)
            parent2 = tournament_selection(evaluated)
            child = crossover(parent1, parent2)
            next_gen.append(child)

        # Step 3: Mutation
        for i in range(len(next_gen)):
            if random.random() < mutation_rate:
                next_gen[i] = mutate(next_gen[i], courses, rooms, weights)

        population = next_gen

    return best_solution, best_cost, cost_history
