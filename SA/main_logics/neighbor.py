import copy
import random

def generate_neighbor(solution, courses, rooms, weights):
    neighbor = copy.deepcopy(solution)
    mutation_type = random.choices(
        ["greedy_improve", "swap", "reroll", "random_shift"],
        weights=[0.6, 0.15, 0.15, 0.1]
    )[0]

    if mutation_type == "greedy_improve":
        class_penalties = {}
        for course_id, course_info in courses.items():
            for cls in course_info["classes"]:
                # assert all(cls["possible_rooms"] for course in courses.values() for cls in course["classes"]), "Some classes have no possible rooms!"
                
                class_id = cls["id"]
                if class_id not in solution:
                    continue
                assignment = solution[class_id]
                room_id = assignment["room"]
                time = assignment["time"]
                penalty = 0

                if cls.get("limit", 0) > rooms[room_id]["capacity"]:
                    penalty += 1000 + (cls["limit"] - rooms[room_id]["capacity"])
                penalty += weights.get("time", 0) * time.get("penalty", 0)

                for room_info in cls["possible_rooms"]:
                    if room_info[0] == room_id:
                        penalty += weights.get("room", 0) * room_info[1]
                        break

                class_penalties[class_id] = penalty

        if not class_penalties:
            return neighbor  # nothing to do

        sorted_classes = sorted(class_penalties.items(), key=lambda x: -x[1])
        class_id = random.choice(sorted_classes[:5])[0]  # Top 5 worst

        for course_id, course_info in courses.items():
            for cls in course_info["classes"]:
                if cls["id"] == class_id:
                    current_assignment = solution[class_id]
                    best_candidate = None
                    best_score = float("inf")

                    for room_id, room_penalty in cls["possible_rooms"]:
                        for time in cls["possible_times"]:
                            if room_id == current_assignment["room"] and time == current_assignment["time"]:
                                continue
                            score = 0
                            score += weights.get("time", 0) * time.get("penalty", 0)
                            score += weights.get("room", 0) * room_penalty
                            if cls.get("limit", 0) > rooms[room_id]["capacity"]:
                                score += 1000 + (cls["limit"] - rooms[room_id]["capacity"])
                            if score < best_score:
                                best_score = score
                                best_candidate = {"room": room_id, "time": time}

                    if best_candidate:
                        neighbor[class_id] = best_candidate
                    break

    elif mutation_type == "swap":
        class_ids = list(solution.keys())
        if len(class_ids) < 2:
            return neighbor
        a, b = random.sample(class_ids, 2)
        neighbor[a], neighbor[b] = neighbor[b], neighbor[a]

    elif mutation_type == "reroll":
        class_ids = list(solution.keys())
        class_id = random.choice(class_ids)
        for course_id, course_info in courses.items():
            for cls in course_info["classes"]:
                if cls["id"] == class_id:
                    if not cls["possible_rooms"] or random.choice(cls["possible_times"]):
                        print(f"⚠️ Skipping class {cls['id']} — no possible rooms or times assigned.")
                        continue
                    new_room, _ = random.choice(cls["possible_rooms"])
                    new_time = random.choice(cls["possible_times"])
                    neighbor[class_id] = {"room": new_room, "time": new_time}
                    break

    elif mutation_type == "random_shift":
        class_ids = list(solution.keys())
        class_id = random.choice(class_ids)
        current = solution[class_id]
        # Shift room or time
        shift_room = random.choice([True, False])
        for course_id, course_info in courses.items():
            for cls in course_info["classes"]:
                if cls["id"] == class_id:
                    if not cls["possible_rooms"] or random.choice(cls["possible_times"]):
                        print(f"⚠️ Skipping class {cls['id']} — no possible rooms or times assigned.")
                        continue
                    
                    if shift_room:
                        new_room, _ = random.choice(cls["possible_rooms"])
                        neighbor[class_id]["room"] = new_room
                    else:
                        new_time = random.choice(cls["possible_times"])
                        neighbor[class_id]["time"] = new_time
                    break

    return neighbor
