from PIL import Image
import numpy as np
from keras.models import load_model
import csv
from io import BytesIO

# Load the image classification model
model = load_model('FV.h5')

def load_nutritional_data(csv_file_path):
    nutritional_data = {}
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nutritional_data[int(row['ClassId'])] = {
                'FoodItem': row['FoodItem'],
                'Calories': float(row['Calories']),
                'Protein': float(row['Protein'])
            }
    return nutritional_data

# Function to process the uploaded image and make predictions
def predict_food_item(image_bytes_io):
    img = Image.open(image_bytes_io).resize((224, 224))
    img_array = np.array(img) / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    return predicted_class


# Function to fetch nutritional information based on predicted class
def fetch_nutritional_info(predicted_class, nutritional_data):
    if predicted_class in nutritional_data:
        food_item_info = nutritional_data[predicted_class]
        return food_item_info['FoodItem'], food_item_info['Calories'], food_item_info['Protein']
    else:
        return None, None, None
