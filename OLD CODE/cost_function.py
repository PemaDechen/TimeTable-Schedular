

def calculate_cost(timetable, data):
    """
    timetable: { event_id: (room_id, timeslot_id) }
    data: parsed from muni-fi-spr16.xml
    """

    weights = data['optimization'] 

    hard_violations = 0
    soft_penalty = 0

    # ------------- HARD CONSTRAINTS CHECKS --------------

    # 1. Student Conflicts: No student attends two classes at same timeslot
    student_schedule = {}
    for event_id, (room_id, timeslot_id) in timetable.items():
        students = data['event_students'][event_id]
        for student in students:
            if (student, timeslot_id) in student_schedule:
                hard_violations += 1
            else:
                student_schedule[(student, timeslot_id)] = event_id

    # 2. Room Capacity Violation
    for event_id, (room_id, timeslot_id) in timetable.items():
        num_students = len(data['event_students'][event_id])
        if num_students > data['rooms'][room_id]:
            hard_violations += 1

    # 3. Available Period Violation
    for event_id, (room_id, timeslot_id) in timetable.items():
        allowed_periods = data['available_periods'].get(event_id, set())
        if allowed_periods and timeslot_id not in allowed_periods:
            hard_violations += 1

    if hard_violations > 0:
        return float('inf')

    # ------------- SOFT CONSTRAINTS CHECKS --------------

    # Room Stability: minimize room changes for the same course
    course_rooms = {}
    for event_id, (room_id, _) in timetable.items():
        course_id = data['event_course'][event_id]
        course_rooms.setdefault(course_id, set()).add(room_id)
    room_stability_penalty = sum(len(rooms) - 1 for rooms in course_rooms.values())

    # Time Compactness: minimize big gaps for students
    time_compactness_penalty = 0
    for student in data['students']:
        student_events = [(timeslot_id, event_id) for event_id, (room_id, timeslot_id) in timetable.items()
                          if student in data['event_students'][event_id]]
        day_events = {}
        for timeslot_id, event_id in student_events:
            day = timeslot_id // data['timeslots_per_day']
            period = timeslot_id % data['timeslots_per_day']
            day_events.setdefault(day, []).append(period)

        for periods in day_events.values():
            periods.sort()
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] > 1:
                    time_compactness_penalty += 1

    # Time Preference Violation
    time_preference_penalty = 0
    for event_id, (room_id, timeslot_id) in timetable.items():
        preferred = data.get('preferred_periods', {}).get(event_id, set())
        if preferred and timeslot_id not in preferred:
            time_preference_penalty += 1

    # Course Distribution: minimize multiple classes of a course on same day
    course_distribution_penalty = 0
    course_days = {}
    for event_id, (room_id, timeslot_id) in timetable.items():
        course_id = data['event_course'][event_id]
        day = timeslot_id // data['timeslots_per_day']
        course_days.setdefault(course_id, set()).add(day)

    for course, days in course_days.items():
        expected_days = len([eid for eid, cid in data['event_course'].items() if cid == course])
        distribution_penalty = expected_days - len(days)
        course_distribution_penalty += max(0, distribution_penalty)

    # ------------- FINAL COST --------------

    soft_penalty = (
        weights['room'] * room_stability_penalty +
        weights['time'] * time_compactness_penalty +
        weights['distribution'] * course_distribution_penalty +
        weights['student'] * time_preference_penalty
    )

    return soft_penalty
