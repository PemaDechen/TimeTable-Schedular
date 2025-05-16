import sys
import os

def output(fileName, data):
    
    output_dir = './output_files' # relative folder inside your project
    os.makedirs(output_dir, exist_ok=True)  # creates output_files/ if it doesn't exist
    
    # Clean up filename (remove unwanted spaces)
    fileName = fileName.strip()

    file_path = os.path.join(output_dir, fileName)

    with open(file_path, "a") as file:
        file.write(str(data))

    print('Output written to', file_path, 'successfully.')