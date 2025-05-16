import math
import copy
import random
from collections import defaultdict
from intitial_solution import initial_solution
from parse_data import courses, rooms, weights, distributions, students, output
from sample_result import result

# Define Simulated Annealing Parameters
initial_temp = 1000
cooling_rate = 0.95
min_temp = 1
max_iterations = 1000

# Cost function (reuse simplified one for now)
from collections import defaultdict


def full_cost_function(solution, courses, rooms, students, weights, distributions):
    # Initial Declaration
    total_penalty = 0
    room_time_tracker = set()
    student_schedule = defaultdict(set)
    distribution_penalty = 0
    # Here
    for course_id, course_info in courses.items():
        for cls in course_info["classes"]:
            class_id = cls["id"]
            if class_id not in solution:
                continue

            assignment = solution[class_id]
            room_id = assignment["room"]
            time = assignment["time"]

            # ⛔️ SAFETY CHECK for unknown room
            if room_id not in rooms:
                print(
                    f"⚠️ Room ID {room_id} not found in rooms dictionary — skipping this class."
                )
                continue

            days = time["days"]
            start = time["start"]
            length = time["length"]
            weeks = time["weeks"]
            time_penalty = time.get("penalty", 0)

            # ─── HARD CONSTRAINTS ───
            for day_index, flag in enumerate(days):
                if flag == "1":
                    for week_index, week_flag in enumerate(weeks):
                        if week_flag == "1":
                            # Room-time conflict
                            key = (room_id, day_index, start, week_index)
                            if key in room_time_tracker:
                                total_penalty += 1000
                            else:
                                room_time_tracker.add(key)

                            # Room unavailable check
                            for un in rooms[room_id]["unavailable"]:
                                if (
                                    un["days"][day_index] == "1"
                                    and un["start"]
                                    <= start
                                    < (un["start"] + un["length"])
                                    and un["weeks"][week_index] == "1"
                                ):
                                    total_penalty += 1000

                            # Student clash check
                            for student_id, enrolled_courses in students.items():
                                if course_id in enrolled_courses:
                                    s_key = (day_index, start, week_index)
                                    if s_key in student_schedule[student_id]:
                                        total_penalty += 1000
                                    else:
                                        student_schedule[student_id].add(s_key)

            # Room capacity violation
            room_capacity = rooms[room_id]["capacity"]
            if cls.get("limit", 0) > room_capacity:
                total_penalty += 1000 + (cls["limit"] - room_capacity)

            # ─── SOFT CONSTRAINTS ───
            total_penalty += weights.get("time", 0) * time_penalty

            for room_info in cls["possible_rooms"]:
                if room_info[0] == room_id:
                    total_penalty += weights.get("room", 0) * room_info[1]
                    break

    # ─── DISTRIBUTION CONSTRAINTS ───
    for dist in distributions:
        if dist["type"] == "SameAttendees":
            same_time = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                time = solution[class_id]["time"]
                current_time_key = (time["days"], time["start"], time["weeks"])
                if same_time is None:
                    same_time = current_time_key
                elif current_time_key != same_time:
                    distribution_penalty += weights.get("distribution", 0)

    total_penalty += distribution_penalty
    return total_penalty


# Generate a neighbor by randomly reassigning one class
def generate_neighbor(solution, courses):
    neighbor = copy.deepcopy(solution)
    class_id = random.choice(list(neighbor.keys()))

    # Find corresponding class
    for course_id, course_info in courses.items():
        for cls in course_info["classes"]:
            if cls["id"] == class_id:
                if cls["possible_rooms"] and cls["possible_times"]:
                    new_room = random.choice(cls["possible_rooms"])[0]
                    new_time = random.choice(cls["possible_times"])
                    neighbor[class_id] = {"room": new_room, "time": new_time}
                break
    return neighbor


# Simulated Annealing main loop
def simulated_annealing(
    initial_solution, courses, students, rooms, weights, distributions
):
    current_solution = initial_solution
    current_cost = full_cost_function(
        current_solution, courses, rooms, students, weights, distributions
    )
    best_solution = current_solution
    best_cost = current_cost
    temperature = initial_temp

    iteration = 0
    while temperature > min_temp and iteration < max_iterations:
        neighbor = generate_neighbor(current_solution, courses)
        neighbor_cost = full_cost_function(
            neighbor, courses, rooms, students, weights, distributions
        )
        delta = neighbor_cost - current_cost

        if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
            current_solution = neighbor
            current_cost = neighbor_cost
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost

        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_cost


# Run Simulated Annealing
final_solution, final_cost = simulated_annealing(
    initial_solution, courses, students, rooms, weights, distributions
)

print("initial_solution", initial_solution)
result(final_solution, "SaResult")
output("finalResult.md", final_solution)
print("This is final cost", final_cost)
