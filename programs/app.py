from weather_api import WeatherApp
from gmail_authentication import GmailAPIAuthentication, Gmail_Sender
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

dotenv_path = os.path.join(os.path.dirname(__file__), '../files/config_files/.env')
load_dotenv(dotenv_path)

def main():
    current_city = "Krakow"
    app = WeatherApp(city=current_city)
    app.fetch_weather_data()    
    logging.info(f"Weather data for {current_city} fetched and saved.")
    send = GmailAPIAuthentication()
    gmail_sender = Gmail_Sender(auth=send)
    gmail_sender.send_email(to=os.getenv("EMAIL_ADDRESS"), subject="Weather report", body_html=app.fetch_weather_data(), attachments=None)
    logging.info(f"Weather report email sent for {current_city}.")

if __name__ == "__main__":
    main()