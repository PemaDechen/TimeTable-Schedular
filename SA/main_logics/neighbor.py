import copy
import random

def generate_neighbor(solution, courses, rooms, weights):
    neighbor = copy.deepcopy(solution)

    #! Step 1: Score each class based on how bad its current assignment is
    class_penalties = {}

    for course_id, course_info in courses.items():
        for cls in course_info["classes"]:
            class_id = cls["id"]
            if class_id not in solution:
                continue
            assignment = solution[class_id]
            room_id = assignment["room"]
            time = assignment["time"]
            penalty = 0

            #TODO:1 Room capacity violation
            if cls.get("limit", 0) > rooms[room_id]["capacity"]:
                #! First mapping the penalty in a manner like more the gap in room capacity more the penalty
                penalty += 1000 + (cls["limit"] - rooms[room_id]["capacity"])

            # Time penalty
            # ! and making sure to map penalty based on our priority given by the data
            # weight is from optimisation block
            penalty += weights.get("time", 0) * time.get("penalty", 0)

            #TODO: 2 Room preference penalty
            for room_info in cls["possible_rooms"]:
                # Room info is coming from course dataset and room_id from solution 
                # possible room's array have 2 value 1st the room_id and next the penalty
                if room_info[0] == room_id:
                    # If penalty attached to possible room is zero than cool or add penalty
                    penalty += weights.get("room", 0) * room_info[1]
                    break

            class_penalties[class_id] = penalty

    #! Step 2: Pick class with highest penalty (or one of the top few)
    sorted_classes = sorted(class_penalties.items(), key=lambda x: -x[1])
    class_id = random.choice(sorted_classes[:5])[0]  # Pick one of top 5 "worst"

    #! Step 3: Assign a better (different) room/time
    for course_id, course_info in courses.items():
        for cls in course_info["classes"]:
            if cls["id"] == class_id:
                current_assignment = solution[class_id]
                best_candidate = None
                best_score = float("inf")
                
                for room_id, room_penalty in cls["possible_rooms"]:
                    for time in cls["possible_times"]:
                        # TODO: Not reassigning to the same room if done loses the purpose of reassignment.
                        if room_id == current_assignment["room"] and time == current_assignment["time"]:
                            continue  # Skip same assignment 

                        # Score this combo
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

    return neighbor
