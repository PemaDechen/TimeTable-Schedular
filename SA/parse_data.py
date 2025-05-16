import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from output_data import output

# Reload and parse the uploaded XML file
file_path = '/Users/pemadechen/Downloads/RESEARCH WORK IMPORTANT/latest_research_work/Data/muni_fi_spr16.xml'
tree = ET.parse(file_path)
root = tree.getroot()

# Initialize data structures
courses = defaultdict(lambda: {"classes": []})
rooms = {}
students = defaultdict(list)
weights = {}
distributions = []


# Extract optimization weights
opt = root.find("optimization")
if opt is not None:
    weights = {k: int(v) for k, v in opt.attrib.items()}

# Extract room data
for room in root.find("rooms").findall("room"):
    room_id = int(room.attrib["id"])
    rooms[room_id] = {
        "capacity": int(room.attrib["capacity"]),
        "unavailable": [],
        "travel": {}
    }
    for travel in room.findall("travel"):
        target = int(travel.attrib["room"])
        cost = int(travel.attrib["value"])
        rooms[room_id]["travel"][target] = cost
    for unavailable in room.findall("unavailable"):
        rooms[room_id]["unavailable"].append({
            "days": unavailable.attrib["days"],
            "start": int(unavailable.attrib["start"]),
            "length": int(unavailable.attrib["length"]),
            "weeks": unavailable.attrib["weeks"]
        })
output('NewRoom.md', rooms)
# Extract course and class data
for course in root.find("courses").findall("course"):
    course_id = int(course.attrib["id"])
    for config in course.findall("config"):
        for subpart in config.findall("subpart"):
            for cls in subpart.findall("class"):
                class_data = {
                    "id": int(cls.attrib["id"]),
                    "limit": int(cls.attrib.get("limit", 0)),
                    "possible_rooms": [],
                    "possible_times": []
                }
                for room in cls.findall("room"):
                    class_data["possible_rooms"].append((int(room.attrib["id"]), int(room.attrib.get("penalty", 0))))
                for time in cls.findall("time"):
                    class_data["possible_times"].append({
                        "days": time.attrib["days"],
                        "start": int(time.attrib["start"]),
                        "length": int(time.attrib["length"]),
                        "weeks": time.attrib["weeks"],
                        "penalty": int(time.attrib.get("penalty", 0))
                    })
                courses[course_id]["classes"].append(class_data)
output('NewCourse.md', courses)

# Extract student enrollments
for student in root.find("students").findall("student"):
    student_id = int(student.attrib["id"])
    for course in student.findall("course"):
        students[student_id].append(int(course.attrib["id"]))
output('NewStudents.md', students)

# Parse distributions
for dist in root.find("distributions").findall("distribution"):
    dist_type = dist.attrib["type"]
    required = dist.attrib.get("required", "false") == "true"
    class_ids = [int(cls.attrib["id"]) for cls in dist.findall("class")]
    distributions.append({
        "type": dist_type,
        "required": required,
        "classes": class_ids
    })
output('Distribution.md', distributions)

# Summarize and return
summary = {
    "num_courses": len(courses),
    "num_rooms": len(rooms),
    "num_students": len(students),
    "num_distributions": len(distributions),
    "weights": weights
}
