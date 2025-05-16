import random
from parse_data import courses, output

# Seed for reproducibility
random.seed(42)

# Generate a random feasible initial solution
# We'll map each class ID to a tuple: (room_id, time_assignment)
initial_solution = {}

for course_id, course_info in courses.items():
    for cls in course_info["classes"]:
        class_id = cls["id"]
        if not cls["possible_rooms"] or not cls["possible_times"]:
            continue  # Skip classes without room or time options
        selected_room = random.choice(cls["possible_rooms"])[0]
        selected_time = random.choice(cls["possible_times"])
        initial_solution[class_id] = {
            "room": selected_room,
            "time": selected_time
        }

# Provide a sample of the initial assignments
sample_solution = dict(list(initial_solution.items()))  
print('This is the length',len(sample_solution))
output('SampleSolution.md', sample_solution)

    