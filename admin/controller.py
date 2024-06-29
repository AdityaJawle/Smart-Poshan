from flask import Flask, jsonify, Response, send_file
from app import app
from io import BytesIO
from reportlab.pdfgen import canvas
from .models import Admin, User
from .report import Report


# API endpoint to fetch all data
@app.route('/fetch-all-data', methods=['GET'])
def fetch_data():
    return User().fetch_all_data()
# API endpoint to update the password of a user
@app.route('/update-password/<school>', methods=['PUT'])
def update_pass(school):
    return User().update_password(school)

# API endpoint to delete a user
@app.route('/delete-user/<school>', methods=['DELETE'])
def del_user(school):
    return User().delete_user(school)

# API endpoint to fetch all data
@app.route('/admin-data', methods=['GET'])
def fetch_ad():
    return Admin().fetch_admin()
# API endpoint to update the password of a user
@app.route('/admin-upd-pass/<username>', methods=['PUT'])
def update_pass_ad(username):
    return Admin().change_password(username)

# API endpoint to delete a user
@app.route('/admin-del/<username>', methods=['DELETE'])
def del_admin(username):
    return Admin().delete_admin(username)



report_instance = Report()  # Create an instance of the Report class

@app.route('/fetch-district/<district>', methods=['GET'])
def fetch_district(district):
    try:
        # Call the fetch_dist method to get user data for the specified district
        result = report_instance.fetch_dist(district)

        # Return the fetched data as a JSON response
        return jsonify(result)

    except Exception as e:
        # Handle exceptions gracefully (log or raise an appropriate error)
        print(f"Error in fetch_district route: {type(e).__name__} - {str(e)}")
        return jsonify({"error": "An error occurred while processing the request"})

@app.route('/fetch-report/<school>/<selectedDate>', methods=['GET'])
def report(school, selectedDate):
    try:
        result = report_instance.get_statistics(school, selectedDate)

        # Check if the result is a Flask response object
        if isinstance(result, Response):
            # If it's a response, return the response directly
            return result

        # If it's a regular JSON-serializable object, jsonify it
        return jsonify(result)

    except Exception as e:
        # Print the error information to the console for debugging
        print(f"Error in report route: {type(e).__name__} - {str(e)}")

        # Return a more detailed error response to the client
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/download-pdf/<school>/<selectedDate>', methods=['GET'])
def download_pdf( school, selectedDate):
        try:
            # Retrieve the report data
            result = report_instance.get_statistics(school, selectedDate)

            # Check if the result is a Flask response object
            if isinstance(result, Response):
                return result  # Return the response directly

            # Generate PDF
            pdf_buffer = report_instance.generate_pdf(result)

            # Send the PDF as a file download response
            return send_file(BytesIO(pdf_buffer),
                             mimetype='application/pdf',
                             download_name='{school}-{selectedDate}.pdf')

        except Exception as e:
            # Handle exceptions gracefully (log or raise an appropriate error)
            print(f"Error in fetch_district route: {type(e).__name__} - {str(e)}")
            return jsonify({"error": "An error occurred while processing the request"})

