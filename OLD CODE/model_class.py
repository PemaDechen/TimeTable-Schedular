class Room:
    def __init__(self, id, capacity, travel_map=None, unavailable_times=None):
        self.id = id
        self.capacity = capacity
        self.travel_map = travel_map or {}
        self.unavailable_times = unavailable_times or []

class TimeAssignment:
    def __init__(self, days, start, length, weeks, penalty):
        self.days = days
        self.start = int(start)
        self.length = int(length)
        self.weeks = weeks
        self.penalty = int(penalty)

class RoomAssignment:
    def __init__(self, room_id, penalty):
        self.room_id = room_id
        self.penalty = int(penalty)

class ClassInstance:
    def __init__(self, class_id, limit, rooms, times):
        self.id = class_id
        self.limit = int(limit)
        self.rooms = rooms  # List of RoomAssignment
        self.times = times  # List of TimeAssignment

class Course:
    def __init__(self, course_id, classes):
        self.id = course_id
        self.classes = classes  # List of ClassInstance

class TimetableData:
    def __init__(self, rooms, courses):
        self.rooms = rooms
        self.courses = courses
