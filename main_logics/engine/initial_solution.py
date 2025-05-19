import random

def generate_random_initial_solution(courses, rooms):
    solution = {}
    room_ids = list(rooms.keys())

    for course_id, course_info in courses.items():
        for cls in course_info["classes"]:
            class_id = cls["id"]
            possible_rooms = cls.get("possible_rooms", [])
            if possible_rooms:
                selected_room = random.choice(possible_rooms)[0]
            else:
                selected_room = random.choice(room_ids)

            # Time should be selected based on available options
            possible_times = cls.get("times", [])
            if possible_times:
                selected_time = random.choice(possible_times)
            else:
                # Fallback time structure
                selected_time = {
                    "days": random.choice(["1000000", "0100000", "0010000"]),
                    "start": random.choice(range(96, 216, 12)),
                    "length": random.choice([22, 34, 46]),
                    "weeks": random.choice(["011110111111110", "111111111111111"]),
                    "penalty": 0,
                }

            solution[class_id] = {
                "room": selected_room,
                "time": selected_time,
            }

    return solution
