import requests
import os
from dotenv import load_dotenv
import logging

log_dir = "../weather_app/files/programs_files"
os.makedirs(log_dir, exist_ok=True)  # Ensure the directory exists
logging.basicConfig(
        filename=f"{log_dir}/weather_app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )

class WeatherApp:
    """
    A  weather module that fetches and logs weather data for a specified city.
    """
    def __init__(self, city: str) -> None:
        dotenv_path = os.path.join(os.path.dirname(__file__), '../files/config_files/.env')
        load_dotenv(dotenv_path)
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.city = city
        self.base_url = "http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        self.complete_url = self.base_url.format(city=self.city, api_key=self.api_key)

    def fetch_weather_data(self) -> str:
        try:
            response = requests.get(self.complete_url, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
            data = response.json()
            # Extract weather data
            temperature = data.get('main', {}).get('temp')
            temp_min = data.get('main', {}).get('temp_min')
            temp_max = data.get('main', {}).get('temp_max')
            pressure = data.get('main', {}).get('pressure')
            humidity = data.get('main', {}).get('humidity')
            wind_speed = data.get('wind', {}).get('speed')
            wind_deg = data.get('wind', {}).get('deg')
            CITY = self.city

            html_report = f"""
<html>
  <body>
    <h3>Weather report from: {CITY}</h3>
    <p>
      Temperature: {temperature} &deg;C<br>
      Min Temperature: {temp_min} &deg;C<br>
      Max Temperature: {temp_max} &deg;C<br>
      Pressure: {pressure} hPa<br>
      Humidity: {humidity} %<br>
      Wind Speed: {wind_speed} m/s<br>
      Wind Direction: {wind_deg}&deg;
    </p>
  </body>
</html>
"""
            return html_report
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError:
            logging.error("Error: Could not connect to the weather service.")
        except requests.exceptions.Timeout:
            logging.error("Error: The request timed out.")
        except Exception as err:
            logging.error(f"An error occurred: {err}")
        return None