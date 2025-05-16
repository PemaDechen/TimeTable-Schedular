import math
import random
import copy
from cost_function import calculate_cost
import json

from parse_datas import parse_dataset
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from output_data import output

def simulated_annealing(data, initial_temp=1000, cooling_rate=0.95, max_iter=1000):
    """
    Runs Simulated Annealing to optimize the timetable
    """
    events = list(data['event_students'].keys())
    rooms = list(data['rooms'].keys())
    all_timeslots = list(range(6 * 5))  # Assuming 6 periods/day, 5 working days (30 slots)

    def random_solution():
        timetable = {}
        for event in events:
            room = random.choice(rooms)
            available_periods = data['available_periods'].get(event, all_timeslots)
            if available_periods:
                timeslot = random.choice(list(available_periods))
            else:
                timeslot = random.choice(all_timeslots)
            timetable[event] = (room, timeslot)
        return timetable

    # Initial solution
    current_solution = random_solution()
    current_cost = calculate_cost(current_solution, data)
    best_solution = copy.deepcopy(current_solution)
    best_cost = current_cost

    temp = initial_temp

    for iteration in range(max_iter):
        # Create neighbor
        neighbor = copy.deepcopy(current_solution)

        event_to_change = random.choice(events)
        room = random.choice(rooms)
        available_periods = data['available_periods'].get(event_to_change, all_timeslots)
        if available_periods:
            timeslot = random.choice(list(available_periods))
        else:
            timeslot = random.choice(all_timeslots)
        neighbor[event_to_change] = (room, timeslot)

        neighbor_cost = calculate_cost(neighbor, data)

        # Acceptance probability
        if neighbor_cost < current_cost:
            accept = True
        else:
            prob = math.exp((current_cost - neighbor_cost) / temp)
            accept = random.random() < prob

        if accept:
            current_solution = neighbor
            current_cost = neighbor_cost

            if neighbor_cost < best_cost:
                best_solution = copy.deepcopy(neighbor)
                best_cost = neighbor_cost

        # Cool down
        temp *= cooling_rate

        # Print progress occasionally
        if iteration % 100 == 0 or iteration == max_iter - 1:
            print(f"Iteration {iteration}: Temp={temp:.2f} | Current Cost={current_cost} | Best Cost={best_cost}")

        # Optional early stopping
        if temp < 1e-3:
            break

    return best_solution, best_cost

parsed_data = parse_dataset("/Users/pemadechen/Documents/latest_research_work/Data/muni_fi_spr16.xml")
# data = json.dumps(parsed_data, indent=2)


# # print('This is data', data)
# output('outputResult.md', str(data))
# best_timetable, best_score = simulated_annealing(parsed_data)

# print("\n🔥 Final Best Timetable 🔥")
# for event_id, (room_id, timeslot_id) in best_timetable.items():
#     print(f"Event {event_id}: Room {room_id}, Timeslot {timeslot_id}")

# print(f"\n🏆 Best Timetable Cost: {best_score}")
