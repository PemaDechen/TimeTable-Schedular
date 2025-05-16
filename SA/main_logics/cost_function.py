from collections import defaultdict


def full_cost_function(solution, courses, rooms, students, weights, distributions):
    # Initial Declaration
    total_penalty = 0
    room_time_tracker = set()
    student_schedule = defaultdict(set)
    distribution_penalty = 0
    min_days_penalty = 0
    min_gap_days = 2  # You can make this configurable
    max_days_penalty = 0
    max_allowed_days = 4
    precedence_penalty = 0
    same_room_penalty = 0
    same_start_penalty = 0
    different_time_penalty = 0

    # We are iterating through course and checking if course is part of solution ones which is part of solution is considered for further analysis
    # We are not directly using courses for source of truth and for comparison purpose with the original data.
    #! So, the idea behind research is not to create a timetable, idea is to create an optimised one.
    #!  Timetable is already present creating an optimised one is the challenge.
    for course_id, course_info in courses.items():
        scheduled_days = set()
        active_days = set()
        for cls in course_info["classes"]:
            class_id = cls["id"]
            if class_id not in solution:
                continue
            # Getting ids of room and time if class is part of the solution
            assignment = solution[class_id]
            room_id = assignment["room"]
            time = assignment["time"]

            # ⛔️ SAFETY CHECK for unknown room
            if room_id not in rooms:
                print(
                    f"⚠️ Room ID {room_id} not found in rooms dictionary — skipping this class."
                )
                continue

            # If the room that is present in the course data and the solution is present in the rooms dataset(checking for safety)
            # Extracting data from the time object.
            days = time["days"]
            start = time["start"]
            length = time["length"]
            weeks = time["weeks"]
            time_penalty = time.get("penalty", 0)

            # ─── HARD CONSTRAINTS ───
            # Days looks like
            # {'days': '0000100', 'start': 204, 'length': 36, 'weeks': '011110111111110'}
            for day_index, flag in enumerate(days):
                if flag == "1":
                    # If the day's flag has 1 then that day is scheduled. day is 7 byte binary value.
                    scheduled_days.add(day_index)
                    active_days.add(day_index)
                    for week_index, week_flag in enumerate(weeks):
                        if (
                            week_flag == "1"
                        ):  # Week is weeks': '011110111111110' 15byte binary (each representing each week)
                            # !1
                            # TODO: This constraint is to check if the room is booked twice
                            # Creating a key having room_id, day_index, starting of the class and week_index.
                            # ! This is room key
                            key = (room_id, day_index, start, week_index)
                            # If the key is present in room_time_tracker twice penalty is added
                            # Like first time key is added to the set
                            # Second time inside the penalty block, high penalty of 1000.
                            if key in room_time_tracker:
                                total_penalty += 1000
                            else:
                                room_time_tracker.add(key)
                            # !2
                            # TODO: This constraint is to check if a room is booked when it is unavailable
                            # Room unavailable check
                            # If a room which is unavailable for a particular week and that room is scheduled for same date, day, time and week than penalty of 1000.
                            for un in rooms[room_id]["unavailable"]:
                                if (
                                    un["days"][day_index] == "1"
                                    and un["start"]
                                    <= start
                                    < (un["start"] + un["length"])
                                    and un["weeks"][week_index] == "1"
                                ):
                                    total_penalty += 1000
                            # !3
                            # TODO: Constraint to check if students clash
                            for student_id, enrolled_courses in students.items():
                                if course_id in enrolled_courses:
                                    # ! This is student key
                                    s_key = (day_index, start, week_index)
                                    if s_key in student_schedule[student_id]:
                                        total_penalty += 1000
                                    else:
                                        student_schedule[student_id].add(s_key)
            # !4
            # TODO: Constraint is to check if the course has minimum 2 gaps in between days
            # Min Days Between Classes => Avoid Cramming all lecture of the same courses into back to back days
            # min_gap_days = 2 (declared at the top)
            if len(scheduled_days) > 1:
                sorted_days = sorted(scheduled_days)
                for i in range(len(sorted_days) - 1):
                    gap = sorted_days[i + 1] - sorted_days[i]

                    # If a subject have less than 2 gaps then penalty according to the data(distribution have penalty set)
                    if gap < min_gap_days:
                        # ! FORMULA
                        min_days_penalty += weights.get("distribution", 0)
            total_penalty += min_days_penalty
            # !5
            # TODO: Constraint is to check if the course has maximum 4 gaps in between days not more than that
            # Compactness => Course should not be scattered around 6 days.
            # max_allowed_days = 4
            if len(active_days) > max_allowed_days:
                # If the course is scattered for more than 4 than penalty according to the decalred penalty and teh gap between active day and max-allowed-days.
                # ! FORMULA
                max_days_penalty += (len(active_days) - max_allowed_days) * weights.get(
                    "distribution", 0
                )
            total_penalty += max_days_penalty

            # TODO: This constraint is to check that room capacity must be greater or equal to the required ones.
            room_capacity = rooms[room_id]["capacity"]
            if cls.get("limit", 0) > room_capacity:
                # ! FORMULA
                total_penalty += 1000 + (cls["limit"] - room_capacity)
            total_penalty += weights.get("time", 0) * time_penalty

            # ─── SOFT CONSTRAINTS ───
            for room_info in cls["possible_rooms"]:
                if room_info[0] == room_id:
                    total_penalty += weights.get("room", 0) * room_info[1]
                    break

    # ─── DISTRIBUTION CONSTRAINTS ───
    for dist in distributions:
        # !6
        # TODO: This constraint to ensure that classes that are to be in the same time must be in same time else penalty. Same time implise that the classes must be in same day, at same start time and at the same week.
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
        # !7
        # TODO:  Ensure that the class that is supposed to preceed must preceed
        if dist["type"] == "Precedence":
            if len(dist["classes"]) >= 2:
                # Precedence block only have one class
                class_A = dist["classes"][0]
                class_B = dist["classes"][1]
                if class_A in solution and class_B in solution:
                    time_A = solution[class_A]["time"]
                    time_B = solution[class_B]["time"]

                    # Basic check — earlier day or earlier start time
                    if (
                        time_A["start"] >= time_B["start"]
                        and time_A["days"] >= time_B["days"]
                    ):
                        precedence_penalty += weights.get("distribution", 0)
        # !8
        #    TODO: Ensuring that the classes that are to be in same room is in same room
        if dist["type"] == "SameRoom":
            used_room = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                current_room = solution[class_id]["room"]
                if used_room is None:
                    used_room = current_room
                elif current_room != used_room:
                    same_room_penalty += weights.get("distribution", 0)
        # !9
        # TODO: Classes that are to start on same time must start on the same time
        if dist["type"] == "SameStart":
            start_time = None
            for class_id in dist["classes"]:
                if class_id not in solution:
                    continue
                current_start = solution[class_id]["time"]["start"]
            if start_time is None:
                start_time = current_start
            elif current_start != start_time:
                same_start_penalty += weights.get("distribution", 0)
        # !10
        # TODO: Class that are supposed to be placed in different times must be in different time.
        if dist["type"] == "DifferentTime":
            seen_times = set()
        for class_id in dist["classes"]:
            if class_id not in solution:
                continue
            time_key = (
                solution[class_id]["time"]["days"],
                solution[class_id]["time"]["start"],
                solution[class_id]["time"]["weeks"],
            )
            if time_key in seen_times:
                different_time_penalty += weights.get("distribution", 0)
            else:
                seen_times.add(time_key)
        total_penalty += same_room_penalty
        total_penalty += precedence_penalty
        total_penalty += distribution_penalty
    return total_penalty
