from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import requests  # Import requests to call the weather API
from waitress import serve

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP MySQL root password is empty. Change if needed.
    'database': 'weather_app'
}

# Function to get database connection
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# OpenWeatherMap API URL and API Key (Replace with your key)
API_KEY = '0d3e7c2f75454795c7f66c7bad89f48b'
  # Replace with your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?q="

# Route to display the home page
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM weather_data")
    data = cursor.fetchall()
    conn.close()
    return render_template('index.html', data=data)

# Route to add weather data from the API
@app.route('/add_weather', methods=['POST'])
def add_weather():
    city = request.form['city']

    # Fetch the weather data from the API
    response = requests.get(f"{BASE_URL}{city}&appid={API_KEY}&units=metric")  # Get temperature in Celsius
    data = response.json()

    if data['cod'] == 200:  # Check if the request was successful
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        
        # Store data in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO weather_data (city, temperature, description) VALUES (%s, %s, %s)",
            (city, temperature, description)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    else:
        return f"City {city} not found!", 404

# For production use with Waitress
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
