import xml.etree.ElementTree as ET
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from output_data import output

# Load and parse the XML file
def parse_dataset(fileName):
    tree = ET.parse(fileName)
    root = tree.getroot()


    # TODO: ROOMS
    rooms = {}

    # ?Locate the <rooms> section
    rooms_element = root.find('rooms')

    # ?Loop through each <room> entry
    for room in rooms_element.findall('room'):
        room_id = int(room.attrib['id'])
        capacity = int(room.attrib['capacity'])
        
        # List to store unavailable times for this room
        unavailable_times = []
        
        # List to store travel costs to other rooms
        travel_penalties = []
        
        # Loop through child elements inside <room> (travel, unavailable)
        for elem in room:
            if elem.tag == 'unavailable':
                unavailable_times.append({
                    'days': elem.attrib['days'],
                    'start': int(elem.attrib['start']),
                    'length': int(elem.attrib['length']),
                    'weeks': elem.attrib['weeks']
                })
            elif elem.tag == 'travel':
                travel_penalties.append({
                    'to_room': int(elem.attrib['room']),
                    'cost': int(elem.attrib['value'])
                })
        
        # Store room information
        rooms[room_id] = {
            'capacity': capacity,
            'unavailable': unavailable_times,
            'travel': travel_penalties
        }
        
    # ?Output the Rooms.
    output('Rooms.md', rooms)

    # TODO : COURSES
    # Prepare a list to store classes
    classes = []

# Locate the <courses> section
    courses_element = root.find('courses')

    # Loop through each <course>
    for course in courses_element.findall('course'):
        course_id = int(course.attrib['id'])
        
        for config in course.findall('config'):
            config_id = int(config.attrib['id'])
            
            for subpart in config.findall('subpart'):
                subpart_id = int(subpart.attrib['id'])
                
                for cls in subpart.findall('class'):
                    class_id = int(cls.attrib['id'])
                    limit = int(cls.attrib['limit'])
                    
                    possible_rooms = []
                    possible_times = []
                    
                    for elem in cls:
                        if elem.tag == 'room':
                            room_id = int(elem.attrib['id'])
                            possible_rooms.append(room_id)
                        
                        if elem.tag == 'time':
                            time_data = {
                                'days': elem.attrib['days'],
                                'start': int(elem.attrib['start']),
                                'length': int(elem.attrib['length']),
                                'weeks': elem.attrib['weeks']
                            }
                            possible_times.append(time_data)
                    
                    # Store everything about this class
                    classes.append({
                        'course_id': course_id,
                        'config_id': config_id,
                        'subpart_id': subpart_id,
                        'class_id': class_id,
                        'limit': limit,
                        'possible_rooms': possible_rooms,
                        'possible_times': possible_times
                    })
    output('Courses.md', classes)
    
    # TODO: OPTIMISATION WEIGHT
    weights = {}

    optimization_element = root.find('optimization')
    if optimization_element is not None:
        weights['time'] = int(optimization_element.attrib.get('time', 0))
        weights['room'] = int(optimization_element.attrib.get('room', 0))
        weights['distribution'] = int(optimization_element.attrib.get('distribution', 0))
        weights['student'] = int(optimization_element.attrib.get('student', 0))

    
    output('Optimised_Weight.md', weights)
    

