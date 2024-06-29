from flask import Flask, render_template, jsonify, request, Response, session, send_file, make_response
from app import app
from app import db
import base64
from PIL import Image
from io import BytesIO
from bson.binary import Binary
from bson import ObjectId
from datetime import datetime, timedelta
from reportlab.platypus import Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader

class Report:
    def fetch_dist(self, district):
        try:
            collection = db['users']
            query = {} if district is None else {'district': district}
            result = list(collection.find(query, {'_id': False}))
            if result:
                return result
            else:
                return {"error": "No data found for the specified district"}
        except Exception as e:
            print(f"Error fetching data: {type(e).__name__} - {str(e)}")
            return {"error": "An error occurred while fetching data"}


    def get_statistics(self, selected_school, selected_date_str):
        try:
            # Parse the selected date to datetime object
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')

            # Fetch data for the selected date from both collections
            meal_data = list(db.meal.find({'school_name': selected_school, 'upload_date': {'$gte': selected_date, '$lt': selected_date + timedelta(days=1)}}))
            student_data = list(db.student_record.find({'school_name': selected_school, 'upload_date': {'$gte': selected_date, '$lt': selected_date + timedelta(days=1)}}))

            # Decode images from bytes format and gather associated data
            meal_images = [{'_id': str(item['_id']),
                            'image': self.decode_image(item['image']),
                            'food_item': item['food_item'],
                            'calories': item['calories'],
                            'protein': item['protein'],
                            'school_name': item['school_name'],
                            'upload_date': item['upload_date']} for item in meal_data]

            student_images = [{'_id': str(item['_id']),
                            'image': self.decode_image(item['image']),
                            'school_name': item['school_name'],
                            'class_name': item['class_name'],
                            'present_count': item['present_count'],
                            'absent_count': item['absent_count'],
                            'upload_date': item['upload_date']} for item in student_data]

            # Generate PDF
            pdf_data = self.generate_pdf(meal_images, student_images)

            # Set up Flask response to send the PDF for download
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename="data_report.pdf"'
            return response

        except Exception as e:
            print(f"Error generating PDF: {type(e).__name__} - {str(e)}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500



    def decode_image(self, image_bytes):
            # Convert bytes to base64 and decode
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return image_base64

    def generate_pdf(self, meal_images, student_images):
            buffer = BytesIO()  # Create a BytesIO buffer to write the PDF content

            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []

            # Define table styles
            style_sheet = getSampleStyleSheet()
            meal_table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black)]
            student_table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black)]

            # Add meal images and data to PDF
            meal_table_data = [["Meal Image", "Food Item", "Calories", "Protein", "School Name", "Upload Date"]]
            for item in meal_images:
                image_data = BytesIO(base64.b64decode(item['image']))  # Decode image data
                image = Image(image_data, width=1.5*inch, height=1.5*inch)  # Resize image to fit within cell
                meal_table_data.append([image, item['food_item'], str(item['calories']), str(item['protein']), item['school_name'], str(item['upload_date'])])

            meal_table = Table(meal_table_data)
            meal_table.setStyle(TableStyle(meal_table_style))
            elements.append(meal_table)

            # Add spacer between tables
            elements.append(Spacer(1, 12))

            # Add student images and data to PDF
            student_table_data = [["Student Image", "School Name", "Class Name", "Present", "Absent", "Upload Date"]]
            for item in student_images:
                image_data = BytesIO(base64.b64decode(item['image']))  # Decode image data
                image = Image(image_data, width=1.5*inch, height=1.5*inch)  # Resize image to fit within cell
                student_table_data.append([image, item['school_name'], item['class_name'], item['present_count'], item['absent_count'], str(item['upload_date'])])

            student_table = Table(student_table_data)
            student_table.setStyle(TableStyle(student_table_style))
            elements.append(student_table)

            doc.build(elements)

            # Seek to the beginning of the buffer
            buffer.seek(0)
            return buffer.getvalue()  # Return the PDF content as bytes

