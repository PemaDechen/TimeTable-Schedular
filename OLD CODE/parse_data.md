# # import xml.etree.ElementTree as ET
# # import sys
# # import os
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# # from output_data import output
# # import json
# # import xml.etree.ElementTree as ET

# # def parse_dataset(xml_path):
# #     tree = ET.parse(xml_path)
# #     root = tree.getroot()

# #     rooms = {}
# #     events = {}
# #     available_periods = {}
# #     preferred_periods = {}
# #     event_course = {}
# #     courses_students = {}
# #     event_students = {}
# #     students_set = set()
# #     timeslots_per_day = 6  

# #     # Parse Rooms
# #     for room in root.find('rooms'):
# #         room_id = int(room.attrib['id'])
# #         capacity = int(room.attrib['capacity'])
# #         rooms[room_id] = capacity

# #     # Parse Courses
# #     course_id_counter = 1
# #     student_id_counter = 1
# #     for course in root.find('courses'):
# #         course_id = int(course.attrib['id'])
# #         student_limit = int(course.attrib.get('limit', 30))  # fallback limit
        
# #         # Simulate enrolling 'student_limit' students in this course
# #         students_for_course = set(range(student_id_counter, student_id_counter + student_limit))
# #         courses_students[course_id] = students_for_course
# #         student_id_counter += student_limit

# #         # Each class inside course is an event
# #         for clazz in course.findall('class'):
# #             event_id = int(clazz.attrib['id'])
# #             events[event_id] = {
# #                 'course_id': course_id,
# #                 'limit': int(clazz.attrib['limit']),
# #             }
# #             event_course[event_id] = course_id
# #             event_students[event_id] = courses_students[course_id]

# #     # Parse Times
# #     for time in root.find('times'):
# #         timeslot_id = int(time.attrib['id'])
# #         for assigned in time.findall('assigned'):
# #             class_id = int(assigned.attrib['class'])
# #             available_periods.setdefault(class_id, set()).add(timeslot_id)
# #         for preferred in time.findall('preferred'):
# #             class_id = int(preferred.attrib['class'])
# #             preferred_periods.setdefault(class_id, set()).add(timeslot_id)

# #     # Collect all students
# #     for students in event_students.values():
# #         students_set.update(students)

# #     # Parse Optimization Weights
# #     optimization = {}
# #     opt_node = root.find('optimization')
# #     if opt_node is not None:
# #         for opt in opt_node:
# #             optimization[opt.tag] = int(opt.attrib['weight'])

# #     data = {
# #         'rooms': rooms,
# #         'events': events,            # event_id mapped to course info
# #         'event_course': event_course, # event_id -> course_id
# #         'event_students': event_students, # event_id -> set(student_ids)
# #         'available_periods': available_periods,
# #         'preferred_periods': preferred_periods,
# #         'students': students_set,
# #         'optimization': optimization,
# #         'timeslots_per_day': timeslots_per_day
# #     }
    
# #     output('data.json', data)

# #     return data



    
    
# 


