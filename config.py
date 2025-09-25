import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Validate required environment variables
def validate_config():
   
    missing_vars = []

    if not SMTP_USER:
        missing_vars.append('SMTP_USER')
    if not SMTP_PASS:
        missing_vars.append('SMTP_PASS')
    if not OPENWEATHER_API_KEY:
        missing_vars.append('OPENWEATHER_API_KEY')

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return True
