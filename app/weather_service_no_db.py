"""
Weather Service - Database-Free Version
Only real-time data, no database operations
"""

import requests
import json
from datetime import datetime, timedelta
import pytz
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

API_KEY = 'ee4046c156c4403db3f172241250107'
BASE_URL = 'http://api.weatherapi.com/v1'

# Dynamic location - can be updated at runtime
def _load_saved_location():
    try:
        from .search import load_location_from_file
        return load_location_from_file()
    except:
        return 'Agno River'  # Default Philippine location

_current_location = _load_saved_location()

def get_location():
    """Get the current location for weather API calls."""
    try:
        from .search import load_location_from_file
        global _current_location
        _current_location = load_location_from_file()
    except:
        pass  # Keep current value if loading fails
    return _current_location

def set_location(location):
    """Set the location for weather API calls."""
    global _current_location
    _current_location = location
    if FLASK_AVAILABLE:
        try:
            current_app.logger.info(f"Weather location updated to: {location}")
        except:
            print(f"Weather location updated to: {location}")
    else:
        print(f"Weather location updated to: {location}")

def fetch_api(endpoint, params):
    """Helper function to make API requests to WeatherAPI."""
    params['key'] = API_KEY
    params['q'] = get_location()  # Use dynamic location
    response = requests.get(f"{BASE_URL}/{endpoint}.json", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

def get_current_weather(location_query=None):
    """Get current weather data - database-free version"""
    try:
        # Use provided location or default to current location
        params = {}
        if location_query:
            params['q'] = location_query
        
        data = fetch_api('current', params)
        current = data['current']
        location = data['location']
        
        # Get current Philippine river name
        current_river = "Agno River"  # Default Philippine river
        is_philippine = True
        
        try:
            from .philippine_river_service import get_current_philippine_river, get_philippine_weather_city
            
            # Get current Philippine river
            philippine_river = get_current_philippine_river()
            current_river = philippine_river
            # Update location to use weather city for API calls
            weather_city = get_philippine_weather_city(philippine_river)
            if not location_query:  # Only update if no specific location was requested
                params['q'] = weather_city
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine location: {e}")
                except:
                    print(f"Error checking Philippine location: {e}")
            else:
                print(f"Error checking Philippine location: {e}")
        
        # Simple weather description (no AI prediction to avoid database dependency)
        prediction_description = f"Weather conditions for {location['name']}.\nCurrent conditions: {current['condition']['text']}."
        
        result = {
            'temperature_c': current['temp_c'],
            'condition': current['condition']['text'],
            'description': prediction_description,
            'river_name': current_river,
            'uv': current['uv'],
            'location': location['name'],
            'is_philippine': is_philippine
        }
        if FLASK_AVAILABLE:
            current_app.logger.info(f"Current Weather: {json.dumps(result, indent=2)}")
        else:
            print(f"Current Weather: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching current weather: {str(e)}")
        else:
            print(f"Error fetching current weather: {str(e)}")
        return None

def get_wind():
    """Get wind data for current location."""
    try:
        data = fetch_api('current', {})
        current = data['current']
        result = {
            'wind_kph': current['wind_kph']
        }
        if FLASK_AVAILABLE:
            current_app.logger.info(f"Wind: {json.dumps(result, indent=2)}")
        else:
            print(f"Wind: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching wind: {str(e)}")
        else:
            print(f"Error fetching wind: {str(e)}")
        return None

def get_astronomy():
    """Get sunrise and sunset times for current location."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        data = fetch_api('astronomy', {'dt': today})
        astro = data['astronomy']['astro']
        result = {
            'sunrise': astro['sunrise'],
            'sunset': astro['sunset']
        }
        if FLASK_AVAILABLE:
            current_app.logger.info(f"Astronomy: {json.dumps(result, indent=2)}")
        else:
            print(f"Astronomy: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching astronomy: {str(e)}")
        else:
            print(f"Error fetching astronomy: {str(e)}")
        return None

def get_7day_overview():
    """Get 7-day overview data for current location."""
    try:
        # Fetch 3 days of historical data
        history_list = []
        for i in range(3):
            date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
            data = fetch_api('history', {'dt': date})
            history_day = data['forecast']['forecastday'][0]
            entry = {
                'date': history_day['date'],
                'day_of_week': datetime.strptime(history_day['date'], '%Y-%m-%d').strftime('%A'),
                'max_temp_c': history_day['day']['maxtemp_c'],
                'min_temp_c': history_day['day']['mintemp_c'],
                'condition': history_day['day']['condition']['text'],
                'icon': get_weather_icon(history_day['day']['condition']['text']),
                'precip_mm': history_day['day']['totalprecip_mm']
            }
            history_list.append(entry)
        history_list.reverse()  # Show from oldest to most recent

        # Fetch 3 days of forecast data
        data = fetch_api('forecast', {'days': 3})
        forecast_days = data['forecast']['forecastday']
        
        # Get current day (today) from forecast data
        current_day = forecast_days[0]
        current_entry = {
            'date': current_day['date'],
            'day_of_week': datetime.strptime(current_day['date'], '%Y-%m-%d').strftime('%A'),
            'max_temp_c': current_day['day']['maxtemp_c'],
            'min_temp_c': current_day['day']['mintemp_c'],
            'condition': current_day['day']['condition']['text'],
            'icon': get_weather_icon(current_day['day']['condition']['text']),
            'precip_mm': current_day['day']['totalprecip_mm']
        }
        
        # Get 2 days after current day
        forecast_list = []
        for day in forecast_days[1:3]:
            entry = {
                'date': day['date'],
                'day_of_week': datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A'),
                'max_temp_c': day['day']['maxtemp_c'],
                'min_temp_c': day['day']['mintemp_c'],
                'condition': day['day']['condition']['text'],
                'icon': get_weather_icon(day['day']['condition']['text']),
                'precip_mm': day['day']['totalprecip_mm']
            }
            forecast_list.append(entry)
        
        # Add a placeholder day to make it 7 days total
        placeholder_day = {
            'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'day_of_week': (datetime.now() + timedelta(days=3)).strftime('%A'),
            'max_temp_c': current_day['day']['maxtemp_c'],
            'min_temp_c': current_day['day']['mintemp_c'],
            'condition': current_day['day']['condition']['text'],
            'icon': get_weather_icon(current_day['day']['condition']['text']),
            'precip_mm': 0.0
        }
        forecast_list.append(placeholder_day)

        # Combine history, current, and forecast
        overview_list = history_list + [current_entry] + forecast_list
        
        if FLASK_AVAILABLE:
            current_app.logger.info(f"7-Day Overview - History: {len(history_list)}, Current: 1, Forecast: {len(forecast_list)}, Total: {len(overview_list)}")
        else:
            print(f"7-Day Overview - History: {len(history_list)}, Current: 1, Forecast: {len(forecast_list)}, Total: {len(overview_list)}")
        return overview_list
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching 7-day overview: {str(e)}")
        else:
            print(f"Error fetching 7-day overview: {str(e)}")
        return []

def get_weather_icon(weather_condition):
    """Map weather conditions to FontAwesome icons."""
    if not weather_condition:
        return 'fas fa-question-circle'
    
    condition = weather_condition.lower()
    
    # Clear conditions
    if condition in ['clear']:
        return 'fas fa-sun'
    
    # Partly Cloudy conditions
    elif condition in ['partly cloudy']:
        return 'fas fa-cloud-sun'
    
    # Cloudy conditions
    elif condition in ['cloudy']:
        return 'fas fa-cloud'
    
    # Overcast conditions
    elif condition in ['overcast']:
        return 'fas fa-cloud'
    
    # Mist conditions
    elif condition in ['mist']:
        return 'fas fa-smog'
    
    # Rain conditions
    elif any(word in condition for word in ['rain', 'drizzle', 'shower']):
        if 'light' in condition:
            return 'fas fa-cloud-rain'
        elif 'heavy' in condition or 'torrential' in condition:
            return 'fas fa-cloud-showers-heavy'
        else:
            return 'fas fa-cloud-rain'
    
    # Thunderstorm conditions
    elif any(word in condition for word in ['thunder', 'thunderstorm']):
        return 'fas fa-bolt'
    
    # Snow conditions
    elif any(word in condition for word in ['snow', 'sleet']):
        return 'fas fa-snowflake'
    
    # Fog conditions
    elif any(word in condition for word in ['fog', 'haze']):
        return 'fas fa-smog'
    
    # Default fallback
    else:
        return 'fas fa-cloud'

def get_weather_background_video(weather_condition):
    """Simplified function to return background video."""
    if FLASK_AVAILABLE:
        current_app.logger.info("Using simplified background video: videos/bg_vdo01.mp4")
    else:
        print("Using simplified background video: videos/bg_vdo01.mp4")
    
    return 'videos/bg_vdo02.mp4'
