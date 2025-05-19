import pandas as pd  # type: ignore
import os
from initial_solution import generate_random_initial_solution
from parse_data import courses, rooms

# Go up one level from engine/ → to main_logics/
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_dir = os.path.join(base_dir, 'output_files', 'final_result')
os.makedirs(output_dir, exist_ok=True)


def result(solution, excelFileName):
    day_map = {
        "1000000": "Monday",
        "0100000": "Tuesday",
        "0010000": "Wednesday",
        "0001000": "Thursday",
        "0000100": "Friday",
        "0000010": "Saturday",
        "0000001": "Sunday",
    }

    # Prepare data for table
    readable_data = []

    for i, (class_id, details) in enumerate(solution.items()):
        # if i >= 20:  # Limit to first 20 entries
        #     break
        time = details["time"]
        day_binary = time["days"]
        readable_day = day_map.get(day_binary, day_binary)  # fallback to raw if unknown
        start_slot = time["start"]
        length_slots = time["length"]
        start_time_minutes = start_slot * 5  # 1 slot = 5 mins
        duration_minutes = length_slots * 5

        start_hour = start_time_minutes // 60
        start_minute = start_time_minutes % 60
        start_time_str = f"{start_hour:02}:{start_minute:02}"

        if duration_minutes >= 60:
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            if minutes > 0:
                duration_str = f"{hours} hr {minutes} min"
            else:
                duration_str = f"{hours} hr"
        else:
            duration_str = f"{duration_minutes} min"

        readable_data.append(
            {
                "Class ID": class_id,
                "Room ID": details["room"],
                "Day": readable_day,
                "Start Time": start_time_str,
                "Duration (min)": duration_minutes,
                "Weeks Active": time["weeks"].count("1"),
                "Penalty": time["penalty"],
                "Proper Time": duration_str,
            }
        )

    # Convert to DataFrame and display
    df_readable = pd.DataFrame(readable_data)
    print(df_readable)

    # Save the file
    file_path = os.path.join(output_dir, f"{excelFileName}.csv")
    df_readable.to_csv(file_path, index=False)


