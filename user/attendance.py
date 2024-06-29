import cv2
from pyzbar.pyzbar import decode
import csv
from pymongo import MongoClient
import os
from app import app
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_poshan']
collection = db['id_cards']

# Fetch data from the database
cursor = collection.find({}, {'_id': 0, 'School Name': 1, 'Roll No': 1, 'Class': 1, 'Name': 1, 'SHAKey': 1})

# Dictionary to store school and class counts
school_class_sha_keys = {}

# Store the data in a temporary variable
temp_school_class_counts = {}

# Group temp_data by school name and class
grouped_data = {}

# Write data to CSV file
for document in cursor:
    school_name = document['School Name']
    roll_no = document['Roll No']
    student_class = document['Class']
    name = document['Name']
    sha_key = document['SHAKey']
    identifier = f"{school_name} - {student_class}"

    # Update school_class_sha_keys
    if identifier in school_class_sha_keys:
        school_class_sha_keys[identifier].add(sha_key)
    else:
        school_class_sha_keys[identifier] = {sha_key}

    # Update temp_school_class_counts
    temp_school_class_counts[identifier] = temp_school_class_counts.get(identifier, 0) + 1

    # Update grouped_data
    school_class = f"{school_name} - {student_class}"
    if school_class in grouped_data:
        grouped_data[school_class].append({
            'school_name': school_name,
            'roll_no': roll_no,
            'student_class': student_class,
            'name': name,
            'sha_key': sha_key,
            'doa': datetime.now().strftime('%Y-%m-%d')  # Add the current date as DOA
        })
    else:
        grouped_data[school_class] = [{
            'school_name': school_name,
            'roll_no': roll_no,
            'student_class': student_class,
            'name': name,
            'sha_key': sha_key,
            'doa': datetime.now().strftime('%Y-%m-%d')  # Add the current date as DOA
        }]

# Print the counts
print("\nSchool Name - Class Counts in temp_data:")
for identifier, count in temp_school_class_counts.items():
    print(f"{identifier}: {count} occurrences")

# Print the grouped data
print("\nGrouped Data:")
for school_class, data_list in grouped_data.items():
    print(f"{school_class}:")
    for data in data_list:
        print(f"   SHA-256 Key: {data['sha_key']}")

# Write data to CSV file
for school_class, data_list in grouped_data.items():
    csv_file_path = f"{school_class.replace(' ', '_')}.csv"
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['School Name', 'Roll No', 'Class', 'Name', 'SHAKey', 'Status', 'DOA'])
        for data in data_list:
            csv_writer.writerow([data['school_name'], data['roll_no'], data['student_class'], data['name'], data['sha_key'], 'Absent', data['doa']])

# Function to read QR code from the camera
def read_qr_code_camera():
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Dictionary to store SHA-256 key status for each school and class combination
    sha_key_status = {}
    qr_code_history = set()

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Decode QR codes
            barcodes = decode(frame)

            # Process each barcode
            for barcode in barcodes:
                # Extract QR code data
                qr_data = barcode.data.decode('utf-8')

                # Split the data using '\n' as the delimiter
                data_list = qr_data.split('\n')

                # Ensure the data has the expected structure
                if len(data_list) >= 6:
                    # Extract relevant information
                    school_name = data_list[1].strip()
                    roll_no = data_list[2].strip()  # Assuming Roll No is at index 0
                    student_class = data_list[3].strip()
                    name = data_list[4].strip()
                    sha_key = data_list[5].strip()

                    # Combine school_name and class for a unique identifier
                    identifier = f"{school_name} - {student_class}"

                    # Check if SHA-256 key is already present for the specific school and class
                    if identifier not in sha_key_status or sha_key not in sha_key_status[identifier]:
                        # Add SHA-256 key to the status dictionary
                        if identifier not in sha_key_status:
                            sha_key_status[identifier] = set()
                        sha_key_status[identifier].add(sha_key)

                    if qr_data in qr_code_history:
                        print("Already Read:", qr_data)
                    else:
                        # Update the QR code history
                        qr_code_history.add(qr_data)

                        # Create a new CSV file if not exists, otherwise append
                        csv_file_path = f"{identifier.replace(' ', '_')}.csv"
                        with open(csv_file_path, 'r') as csvfile:
                            reader = csv.reader(csvfile)
                            rows = list(reader)
                            for i, row in enumerate(rows):
                                if row[4] == sha_key:
                                    rows[i][-2] = 'Present'  # Add the current date/time
                                    break

                        with open(csv_file_path, 'w', newline='') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerows(rows)

                        for updated_row in rows[1:]:
                            attendance = {
                                'school_name': updated_row[0],
                                'roll_no': updated_row[1],
                                'student_class': updated_row[2],
                                'name': updated_row[3],
                                'sha_key': updated_row[4],
                                'attendance_status': updated_row[-2],
                                'attendance_date': updated_row[-1]
                            }
                            db.attendance.insert_one(attendance)

                else:
                    print(f"Invalid QR Code Data: {qr_data}")

            # Display the frame
            cv2.imshow('QR Code Scanner', frame)

            # Check for key press events
            key = cv2.waitKey(1)
            if key == ord('r') and cv2.waitKey(1) & 0xFF == 0x4000002E:
                # Set the flag to exit the loop
                break

    except KeyboardInterrupt:
        print("Scanning stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Release the camera and close the window
        cap.release()
        cv2.destroyAllWindows()


# Call the function to read QR code from the camera
read_qr_code_camera()

# After exiting the QR code loop, start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
