from flask import Flask, request, jsonify, session, Response
from .models import User
from app import app, db
import os
from io import BytesIO
import base64
from datetime import datetime
from .image_pd import predict_food_item
from .image_pd import load_nutritional_data, predict_food_item, fetch_nutritional_info
from .id_cards import Image, ImageDraw, ImageFont, qrcode, save_bmp, save_png, save_to_csv, save_to_mongodb, generate_next_idno, calculate_sha_key, get_school_name
from .attendance import  cv2, decode, csv



# Load nutritional data from the CSV file
CSV_FILE_PATH = 'nutritional_data.csv'
nutritional_data = load_nutritional_data(CSV_FILE_PATH)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

@app.route('/user/adsignup', methods=['POST'])
def asignup():
    return User().adsignup()

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()

@app.route('/user/admin', methods=['POST'])
def admin():
    return User().admin()

UPLOAD_FOLDER = 'static/uploads'

def generate_unique_filename():
    return datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'

def process_image_upload(uploaded_file,nutritional_data):

    if uploaded_file.filename != '':
        unique_filename = generate_unique_filename()
        uploaded_image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        image_bytes = uploaded_file.read()
        predicted_class = predict_food_item(BytesIO(image_bytes))
        food_item, calories, protein = fetch_nutritional_info(predicted_class, nutritional_data)

        school_name = get_school_name()

        meal_data = {
            'image': image_bytes,  # Save the image as bytes
            'food_item': food_item,
            'calories': calories,
            'protein': protein,
            'school_name': school_name,
            'upload_date': datetime.now()
        }
        db.meal.insert_one(meal_data)

        # Convert image bytes to base64
        image_data = base64.b64encode(image_bytes).decode('utf-8')

        return food_item, calories, protein, uploaded_image_path, image_data
    return None, None, None, None, None


@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    fname = data['fname']
    lname = data['lname']
    roll_no = data['roll_no']
    height = data['height']
    weight = data['weight']
    student_class = data['studentClass']
    bmi = round(weight / ((height / 100) ** 2), 2)
    school_name = get_school_name()

    students_collection = db.students
    students_collection.insert_one({
        'fname': fname,
        'lname': lname,
        'roll_no': roll_no,
        'height': height,
        'weight': weight,
        'student_class': student_class,
        'bmi': bmi,
        'school_name': school_name
    })

    return jsonify({"message": "Student added successfully"})

@app.route('/get_class_data/<selected_class>', methods=['GET'])
def get_class_data(selected_class):
    school_name = get_school_name()
    students_collection = db.students
    class_data = students_collection.find(
        {'student_class': selected_class, 'school_name': school_name},
        {'_id': 0, 'fname': 1, 'lname': 1, 'roll_no': 1, 'height': 1, 'weight': 1, 'bmi': 1}
    )

    return jsonify(list(class_data))

@app.route('/generate_id_card', methods=['POST'])
def generate_id_card():
    if request.method == 'POST':
        data = request.json
        fname = data['fname']
        roll_no = data['roll_no']
        student_class = data['studentClass']
        school_name = get_school_name()
        

        # Create a portrait format image
        image = Image.new('RGB', (800, 1200), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Generate a unique ID
        idno = generate_next_idno(school_name)
        sha_key = calculate_sha_key(idno, fname, school_name)

        # Create a portrait format image
        image = Image.new('RGB', (800, 1200), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Change the font to Times New Roman
        font = ImageFont.truetype('times.ttf', size=45)

        # adding a unique id number. You can manually take it from the user
        id_position = (50, 150)
        roll_no_position = (50, 500)
        class_position = (50, 600)
        name_position = (50, 700)
        qr_position = (50, 300)

        # For the ID
        (x, y) = id_position
        message = str('ID: ' + str(idno))
        color = 'rgb(0, 0, 0)'  # black color
        font = ImageFont.truetype('times.ttf', size=60)
        draw.text((x, y), message, fill=color, font=font)

        # For the Roll Number
        (x, y) = roll_no_position
        roll_no = data['roll_no']
        froll_no = str('Roll No: ' + str(roll_no))
        color = 'rgb(0, 0, 0)'  # black color
        draw.text((x, y), froll_no, fill=color, font=font)

        # For the Class
        (x, y) = class_position
        student_class = data['studentClass']
        fstudent_class = str('Class: ' + str(student_class))
        draw.text((x, y), fstudent_class, fill=color, font=font)

        # For the Name
        (x, y) = name_position
        fname = data['fname']
        ename = str('Name: ' + str(fname))
        draw.text((x, y), ename, fill=color, font=font)

        # Create QR code
        QR = qrcode.make(str(idno) + '\n' + str(school_name) +'\n' + str(roll_no) +'\n' + str(student_class) + '\n' + str(fname) + '\n' + str(sha_key))

        # Save QR code as BMP
        QR_file = save_bmp(QR, idno, school_name)

        # Open the BMP file
        QR = Image.open(QR_file)

        # Paste QR code onto the image at the fixed position
        image.paste(QR, qr_position)

        # Save details to CSV
        details = {
            'ID': idno,
            'School Name': school_name,
            'Roll No': roll_no,
            'Class': student_class,
            'Name': fname,
            'SHAKey': sha_key
        }
        save_to_csv(details, school_name)

        save_to_mongodb(details, school_name)

        # Save the edited image as PNG
        png_file = save_png(image, fname, school_name)
        return png_file
    

    

@app.route('/attendance-statistics/<school_name>/<student_class>', methods=['GET'])
def get_attendance_statistics(school_name, student_class):
    try:
        # Get today's date in the format 'YYYY-MM-DD'
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Count unique school_names
        school_name = get_school_name()
        # print("School Name:", school_name)
        result = {'school_details': []}

        # Ensure school_name is a list
        school_name_list = [school_name]

        # For each school, count unique classes and attendance
        for school in school_name_list:
            unique_classes = db.attendance.distinct('student_class', {'school_name': school, 'attendance_date': today_date})
            total_classes = len(unique_classes)

            school_details = {
                'school_name': school,
                'total_classes': total_classes,
                'class_details': []
            }

            for student_class in unique_classes:
                present_count = db.attendance.count_documents({
                    'school_name': school,
                    'student_class': student_class,
                    'attendance_status': 'Present',
                    'attendance_date': today_date
                })
                absent_count = db.attendance.count_documents({
                    'school_name': school,
                    'student_class': student_class,
                    'attendance_status': 'Absent',
                    'attendance_date': today_date
                })

                class_details = {
                    'class_name': student_class,
                    'present_count': present_count,
                    'absent_count': absent_count
                }

                school_details['class_details'].append(class_details)

            result['school_details'].append(school_details)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/attendance-statistics', methods=['GET'])
def get_attendance_statistics_route():
    try:
        statistics = get_attendance_statistics()
        return jsonify(statistics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-image/<school_name>/<student_class>', methods=['POST'])
def upload_image(school_name, student_class):
    try:
        # Get today's date in the format 'YYYY-MM-DD'
        today_date = datetime.now().strftime('%Y-%m-%d')

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = f"{school_name}_{student_class}.jpg"

            # Read the image bytes before saving the file
            image_bytes = file.read()

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.seek(0)  # Reset file pointer to the beginning
            file.save(file_path)

            print(f"File name: {filename}")
            print("File read successful.")

            # Fetch present_count and absent_count from db.attendance
            present_count = db.attendance.count_documents({
                'school_name': school_name,
                'student_class': student_class,
                'attendance_status': 'Present',
                'attendance_date': today_date
            })
            absent_count = db.attendance.count_documents({
                'school_name': school_name,
                'student_class': student_class,
                'attendance_status': 'Absent',
                'attendance_date': today_date
            })

            
            # Save attendance statistics data to MongoDB
            attendance_statistics_data = {
                'image': image_bytes,  # Save the image as bytes
                'school_name': school_name,
                'class_name': student_class,
                'present_count': present_count,
                'absent_count': absent_count,
                'upload_date': datetime.now()
            }
            db.student_record.insert_one(attendance_statistics_data)
            print("MongoDB Insert Successful,")

            # Convert image bytes to base64
            stu_image_data = base64.b64encode(image_bytes).decode('utf-8')

            return jsonify({'message': 'File uploaded successfully', 'stu_image_data': stu_image_data,
                            'present_count': present_count,
                            'absent_count': absent_count}), 200

    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

