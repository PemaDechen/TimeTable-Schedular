from collections import defaultdict

def full_cost_function(solution, courses, rooms, students, weights, distributions):
    total_penalty = 0
    room_time_tracker = set()
    student_schedule = defaultdict(set)

    min_gap_days = 2
    max_allowed_days = 4

    penalty_break_down = {
        "room_time_tracker_penalty": 0,
        "unavailable_room_penalty": 0,
        "student_schedule_penalty": 0,
        "min_days_penalty": 0,
        "max_days_penalty": 0,
        "room_capacity_penalty": 0,
        "soft_time_penalty": 0,
        "possible_room_penalty": 0,
        "distribution_penalty": 0,
        "precedence_penalty": 0,
        "same_room_penalty": 0,
        "same_start_penalty": 0,
        "different_time_penalty": 0,
    }

    for course_id, course_info in courses.items():
        scheduled_days = set()
        active_days = set()

        for cls in course_info["classes"]:
            class_id = cls["id"]
            if class_id not in solution:
                continue

            assignment = solution[class_id]
            room_id = assignment["room"]
            time = assignment["time"]

            if room_id not in rooms:
                print(f"⚠️ Room ID {room_id} not found — skipping this class.")
                continue

            days = time["days"]
            start = time["start"]
            length = time["length"]
            weeks = time["weeks"]
            time_penalty = time.get("penalty", 0)

            for day_index, flag in enumerate(days):
                if flag == "1":
                    scheduled_days.add(day_index)
                    active_days.add(day_index)

                    for week_index, week_flag in enumerate(weeks):
                        if week_flag == "1":
                            key = (room_id, day_index, start, week_index)
                            if key in room_time_tracker:
                                penalty_break_down["room_time_tracker_penalty"] += 1000
                                total_penalty += 1000
                            else:
                                room_time_tracker.add(key)

                            for un in rooms[room_id]["unavailable"]:
                                if (
                                    un["days"][day_index] == "1"
                                    and un["start"] <= start < (un["start"] + un["length"])
                                    and un["weeks"][week_index] == "1"
                                ):
                                    penalty_break_down["unavailable_room_penalty"] += 1000
                                    total_penalty += 1000

                            for student_id, enrolled_courses in students.items():
                                if course_id in enrolled_courses:
                                    s_key = (day_index, start, week_index)
                                    if s_key in student_schedule[student_id]:
                                        penalty_break_down["student_schedule_penalty"] += 1000
                                        total_penalty += 1000
                                    else:
                                        student_schedule[student_id].add(s_key)

            if len(scheduled_days) > 1:
                sorted_days = sorted(scheduled_days)
                for i in range(len(sorted_days) - 1):
                    gap = sorted_days[i + 1] - sorted_days[i]
                    if gap < min_gap_days:
                        penalty = weights.get("distribution", 0)
                        penalty_break_down["min_days_penalty"] += penalty
                        total_penalty += penalty

            if len(active_days) > max_allowed_days:
                penalty = (len(active_days) - max_allowed_days) * weights.get("distribution", 0)
                penalty_break_down["max_days_penalty"] += penalty
                total_penalty += penalty

            if cls.get("limit", 0) > rooms[room_id]["capacity"]:
                excess = cls["limit"] - rooms[room_id]["capacity"]
                penalty = 1000 + excess
                penalty_break_down["room_capacity_penalty"] += penalty
                total_penalty += penalty

            # Soft time penalty
            soft_time_penalty = weights.get("time", 0) * time_penalty
            penalty_break_down["soft_time_penalty"] += soft_time_penalty
            total_penalty += soft_time_penalty

            # Soft room penalty
            for room_info in cls["possible_rooms"]:
                if room_info[0] == room_id:
                    penalty = weights.get("room", 0) * room_info[1]
                    penalty_break_down["possible_room_penalty"] += penalty
                    total_penalty += penalty
                    break

    for dist in distributions:
        if dist["type"] == "SameAttendees":
            same_time = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                time = solution[class_id]["time"]
                key = (time["days"], time["start"], time["weeks"])
                if same_time is None:
                    same_time = key
                elif key != same_time:
                    penalty = weights.get("distribution", 0)
                    penalty_break_down["distribution_penalty"] += penalty
                    total_penalty += penalty

        if dist["type"] == "Precedence":
            if len(dist["classes"]) >= 2:
                class_A, class_B = dist["classes"][:2]
                if class_A in solution and class_B in solution:
                    time_A = solution[class_A]["time"]
                    time_B = solution[class_B]["time"]
                    if (
                        time_A["start"] >= time_B["start"]
                        and time_A["days"] >= time_B["days"]
                    ):
                        penalty = weights.get("distribution", 0)
                        penalty_break_down["precedence_penalty"] += penalty
                        total_penalty += penalty

        if dist["type"] == "SameRoom":
            used_room = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                room = solution[class_id]["room"]
                if used_room is None:
                    used_room = room
                elif room != used_room:
                    penalty = weights.get("distribution", 0)
                    penalty_break_down["same_room_penalty"] += penalty
                    total_penalty += penalty

        if dist["type"] == "SameStart":
            start_time = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                start = solution[class_id]["time"]["start"]
                if start_time is None:
                    start_time = start
                elif start != start_time:
                    penalty = weights.get("distribution", 0)
                    penalty_break_down["same_start_penalty"] += penalty
                    total_penalty += penalty

        if dist["type"] == "DifferentTime":
            seen = set()
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                t = solution[class_id]["time"]
                key = (t["days"], t["start"], t["weeks"])
                if key in seen:
                    penalty = weights.get("distribution", 0)
                    penalty_break_down["different_time_penalty"] += penalty
                    total_penalty += penalty
                else:
                    seen.add(key)

    return total_penalty, penalty_break_down
