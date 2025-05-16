import xml.etree.ElementTree as ET
import sys
import os
import json

def parse_dataset(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rooms = {}
    events = {}
    available_periods = {}
    preferred_periods = {}
    event_course = {}
    courses_students = {}
    event_students = {}
    students_set = set()
    timeslots_per_day = 288

    # Parse Rooms
    rooms_node = root.find('rooms')
    if rooms_node is not None:
        for room in rooms_node.findall('room'):
            room_id = int(room.attrib['id'])
            capacity = int(room.attrib['capacity'])
            rooms[room_id] = capacity

    # Parse Courses
    courses_node = root.find('courses')
    if courses_node is not None:
        course_id_counter = 1
        student_id_counter = 1
        for course in courses_node.findall('course'):
            course_id = int(course.attrib['id'])
            # student_limit = int(course.attrib.get('limit', 30)) #course.find('config').find('subpart').find('class').attrib.get('limit', 30)
            # Find the first 'class' element and extract the limit from there
            student_limit = 30  # Default value
            for config in course.findall('config'):
                for subpart in config.findall('subpart'):
                    class_element = subpart.find('class')
                    if class_element is not None:
                        student_limit = int(class_element.attrib.get('limit', 30))
                        break  # Stop searching after finding the first limit
                if student_limit != 30:  # If limit was found, break the outer loop as well
                    break

            # Simulate enrolling 'student_limit' students in this course
            students_for_course = set(range(student_id_counter, student_id_counter + student_limit))
            # courses_students[course_id] = students_for_course
            courses_students[course_id] = list(students_for_course) # Convert set to list
            student_id_counter += student_limit

            # Each class inside course is an event
            for config in course.findall('config'):
                for subpart in config.findall('subpart'):
                    for clazz in subpart.findall('class'):
                        event_id = int(clazz.attrib['id'])
                        events[event_id] = {
                            'course_id': course_id,
                            'limit': int(clazz.attrib['limit']),
                        }
                        event_course[event_id] = course_id
                        # event_students[event_id] = courses_students[course_id]
                        event_students[event_id] = list(courses_students[course_id])

    # Parse Times
    times_node = root.find('times')
    if times_node is not None:
        for time in times_node.findall('time'):
            timeslot_id = int(time.attrib['id'])
            for assigned in time.findall('assigned'):
                class_id = int(assigned.attrib['class'])
                # available_periods.setdefault(class_id, set()).add(timeslot_id)
                available_periods.setdefault(class_id, []).append(timeslot_id) # Use list instead of set
            for preferred in time.findall('preferred'):
                class_id = int(preferred.attrib['class'])
                # preferred_periods.setdefault(class_id, set()).add(timeslot_id)
                preferred_periods.setdefault(class_id, []).append(timeslot_id) # Use list instead of set

    # Collect all students
    for students in event_students.values():
        students_set.update(students)

    # Parse Optimization Weights
    optimization = {}
    opt_node = root.find('optimization')
    if opt_node is not None:
        for opt in opt_node:
            optimization[opt.tag] = int(opt.attrib['weight'])

    data = {
        'rooms': rooms,
        'events': events,
        'event_course': event_course,
        'event_students': event_students,
        'available_periods': available_periods,
        'preferred_periods': preferred_periods,
        'students': list(students_set), # Convert set to list
        'optimization': optimization,
        'timeslots_per_day': timeslots_per_day
    }

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    return data