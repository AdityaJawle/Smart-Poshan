from flask import Flask, render_template, jsonify, request
from app import db
from passlib.hash import pbkdf2_sha256

class Admin:
    

    def fetch_admin(self):
        try:
            collection = db['admin']

            # Query the database to get all documents
            result = list(collection.find({}, {'_id': False}))

            # Check if data is found
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "No data found"})

        except Exception as e:
            print(f"Error fetching data: {e}")
            return jsonify({"error": "An error occurred while fetching data"})

    def change_password(self, username):
        try:
            collection = db['admin']

            # Get the new password from the request data
            new_password = request.json.get('new_password')

            # Hash the new password before updating
            hashed_password = pbkdf2_sha256.encrypt(new_password)

            # Update the password for the specified user
            result = collection.update_one({'username': username}, {'$set': {'password': hashed_password}})

            if result.modified_count > 0:
                return jsonify({"message": "Password updated successfully"})
            else:
                return jsonify({"error": "User not found or password not updated"})

        except Exception as e:
            print(f"Error updating password: {e}")
            return jsonify({"error": "An error occurred while updating password"})

    def delete_admin(self, username):
        try:
            collection = db['admin']

            # Delete the user by username
            result = collection.delete_one({'username': username})

            if result.deleted_count > 0:
                return jsonify({"message": f"User '{username}' deleted successfully"})
            else:
                return jsonify({"error": f"User '{username}' not found or not deleted"})

        except Exception as e:
            print(f"Error deleting user: {e}")
            return jsonify({"error": "An error occurred while deleting user"})


class User:

    def fetch_all_data(self):
        try:
            collection = db['users']

            # Query the database to get all documents
            result = list(collection.find({}, {'_id': False}))

            # Check if data is found
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "No data found"})

        except Exception as e:
            print(f"Error fetching data: {e}")
            return jsonify({"error": "An error occurred while fetching data"})

    def update_password(self, school):
        try:
            collection = db['users']

            # Get the new password from the request data
            new_password = request.json.get('new_password')

            # Hash the new password before updating
            hashed_password = pbkdf2_sha256.encrypt(new_password)

            # Update the password for the specified user
            result = collection.update_one({'school': school}, {'$set': {'password': hashed_password}})

            if result.modified_count > 0:
                return jsonify({"message": "Password updated successfully"})
            else:
                return jsonify({"error": "User not found or password not updated"})

        except Exception as e:
            print(f"Error updating password: {e}")
            return jsonify({"error": "An error occurred while updating password"})

    def delete_user(self, school):
        try:
            collection = db['users']

            # Delete the user by school
            result = collection.delete_one({'school': school})

            if result.deleted_count > 0:
                return jsonify({"message": f"User '{school}' deleted successfully"})
            else:
                return jsonify({"error": f"User '{school}' not found or not deleted"})

        except Exception as e:
            print(f"Error deleting user: {e}")
            return jsonify({"error": "An error occurred while deleting user"})