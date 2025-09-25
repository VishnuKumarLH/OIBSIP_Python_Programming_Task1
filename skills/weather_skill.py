import requests
import logging
from config import OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)

class WeatherSkill:
   

    def __init__(self):
      
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
       
        if not city or not city.strip():
            return False, "Please specify a city name"

        if not self.api_key:
            return False, "OpenWeatherMap API key not configured. Please check your .env file."

        try:
            # Prepare API request parameters
            params = {
                'q': city.strip(),
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }

            logger.info(f"Fetching weather data for {city}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if city was found
            if data.get('cod') != 200:
                return False, f"City '{city}' not found. Please check the spelling."

            # Extract weather information
            weather_info = self._parse_weather_data(data)

            logger.info(f"Weather data retrieved for {city}: {weather_info}")
            return True, weather_info

        except requests.exceptions.Timeout:
            logger.error("Weather API request timed out")
            return False, "Weather service is taking too long to respond. Please try again."

        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to weather service")
            return False, "Unable to connect to weather service. Please check your internet connection."

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from weather API: {e}")
            return False, "Weather service is currently unavailable. Please try again later."

        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return False, f"An unexpected error occurred while fetching weather data: {str(e)}"

    def _parse_weather_data(self, data):
       
        try:
            city_name = data.get('name', 'Unknown')
            country = data.get('sys', {}).get('country', '')
            location = f"{city_name}, {country}" if country else city_name

            # Get main weather data
            main = data.get('main', {})
            temperature = main.get('temp', 'N/A')
            feels_like = main.get('feels_like', 'N/A')
            humidity = main.get('humidity', 'N/A')
            pressure = main.get('pressure', 'N/A')

            # Get weather description
            weather_list = data.get('weather', [])
            if weather_list:
                description = weather_list[0].get('description', 'N/A').title()
            else:
                description = 'N/A'

            # Get wind information
            wind = data.get('wind', {})
            wind_speed = wind.get('speed', 'N/A')

            # Format the response
            weather_info = f"Weather in {location}: "
            weather_info += f"{temperature}°C, {description}. "
            weather_info += f"Feels like {feels_like}°C. "
            weather_info += f"Humidity: {humidity}%, Pressure: {pressure} hPa, Wind: {wind_speed} m/s."

            return weather_info

        except Exception as e:
            logger.error(f"Error parsing weather data: {e}")
            return "Unable to parse weather information"

    def get_weather_by_coordinates(self, lat, lon):
       
        if not self.api_key:
            return False, "OpenWeatherMap API key not configured. Please check your .env file."

        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            logger.info(f"Fetching weather data for coordinates ({lat}, {lon})")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            weather_info = self._parse_weather_data(data)

            return True, weather_info

        except Exception as e:
            logger.error(f"Error fetching weather by coordinates: {e}")
            return False, f"Unable to get weather for these coordinates: {str(e)}"

    def test_api_key(self):
      
        if not self.api_key:
            return False, "API key not configured"

        try:
            # Make a test request with a known city
            params = {
                'q': 'London',
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 401:
                return False, "Invalid API key. Please check your OpenWeatherMap API key."

            elif response.status_code == 200:
                return True, "API key is valid"

            else:
                return False, f"API key test failed with status code: {response.status_code}"

        except Exception as e:
            return False, f"API key test failed: {str(e)}"
