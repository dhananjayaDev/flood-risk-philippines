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
# Load location from file if it exists, otherwise use default
def _load_saved_location():
    try:
        from .search import load_location_from_file
        return load_location_from_file()
    except:
        return 'Agno River'  # Default Philippine location

_current_location = _load_saved_location()

def get_location():
    """Get the current location for weather API calls."""
    # Always reload from file to get the latest saved location
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

# For backward compatibility
LOCATION = 'Agno River'  # This is now just a default, not used in API calls

def fetch_api(endpoint, params):
    """
    Helper function to make API requests to WeatherAPI.
    """
    params['key'] = API_KEY
    params['q'] = get_location()  # Use dynamic location
    response = requests.get(f"{BASE_URL}/{endpoint}.json", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

def get_current_weather(location_query=None):
    """
    Function to fetch and return current weather data for specified location or current location.
    Returns a dictionary with temperature, condition, UV index, location, and river name.
    """
    try:
        # Use provided location or default to current location
        params = {}
        if location_query:
            params['q'] = location_query
        
        data = fetch_api('current', params)
        current = data['current']
        location = data['location']
        
        # Get current river name based on location (check for Philippine rivers first)
        current_river = "Kalu Ganga (Ratnapura)"  # Default Sri Lankan river
        is_philippine = False
        
        try:
            from .philippine_river_service import get_current_philippine_river, get_philippine_weather_city
            
            # Check if current location is a Philippine river
            philippine_river = get_current_philippine_river()
            # Always use the Philippine river (including default Agno River)
            is_philippine = True
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
        
        # If not Philippine, use Sri Lankan river system
        if not is_philippine:
            try:
                from .river import get_current_river
                current_river = get_current_river()
            except:
                current_river = "Kalu Ganga (Ratnapura)"
        
        # Get flood risk prediction for description
        try:
            from .flood_risk_predictor import predict_flood_risk, format_prediction_for_display
            prediction = predict_flood_risk(hours_back=24)
            if prediction and prediction.get('risk_level') != 'UNKNOWN':
                formatted_prediction = format_prediction_for_display(prediction)
                # Create concise 2-line description for weather UI
                risk_level = formatted_prediction['risk_level']
                confidence = formatted_prediction['confidence']
                primary_factors = prediction.get('primary_factors', [])
                
                # First line: Risk level and confidence
                line1 = f"Flood Risk: {risk_level} (Confidence: {confidence}%)"
                
                # Second line: Top 2 primary factors or key insight
                if primary_factors:
                    if len(primary_factors) >= 2:
                        line2 = f"{primary_factors[0]}. {primary_factors[1]}."
                    else:
                        line2 = f"{primary_factors[0]}."
                else:
                    line2 = formatted_prediction['risk_description']
                
                prediction_description = f"{line1}\n{line2}"
            else:
                prediction_description = 'Flood risk assessment unavailable.\nHeavy rain, strong winds, and occasional lightning expected.'
        except Exception as e:
            prediction_description = f'Flood risk assessment error: {str(e)}.\nHeavy rain, strong winds, and occasional lightning expected.'
        
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

def get_weather_for_location(location_query):
    """
    Function to fetch comprehensive weather data for a specific location.
    Returns a dictionary with all weather parameters.
    """
    try:
        # Fetch current weather data
        current_data = fetch_api('current', {'q': location_query})
        current = current_data['current']
        location = current_data['location']
        
        # Fetch astronomy data for sunrise/sunset
        today = datetime.now().strftime('%Y-%m-%d')
        astronomy_data = fetch_api('astronomy', {'q': location_query, 'dt': today})
        astro = astronomy_data['astronomy']['astro']
        
        result = {
            'location': location['name'],
            'timestamp': datetime.now(pytz.timezone('Asia/Colombo')),
            'temperature_c': current.get('temp_c', 0.0),
            'humidity': current.get('humidity', 0.0),
            'precip_mm': current.get('precip_mm', 0.0),
            'pressure_mb': current.get('pressure_mb', 0.0),
            'wind_kph': current.get('wind_kph', 0.0),
            'wind_dir': current.get('wind_dir', 'N'),
            'uv_index': current.get('uv', 0.0),
            'condition': current.get('condition', {}).get('text', 'Unknown'),
            'feelslike_c': current.get('feelslike_c', 0.0),
            'cloud': current.get('cloud', 0.0),
            'visibility_km': current.get('vis_km', 0.0),
            'gust_kph': current.get('gust_kph', 0.0),
            'sunrise': astro.get('sunrise', '06:00 AM'),
            'sunset': astro.get('sunset', '06:00 PM')
        }
        
        if FLASK_AVAILABLE:
            current_app.logger.info(f"Weather for {location['name']}: {json.dumps(result, indent=2)}")
        else:
            print(f"Weather for {location['name']}: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching weather for {location_query}: {str(e)}")
        else:
            print(f"Error fetching weather for {location_query}: {str(e)}")
        return None

def get_wind():
    """
    Function to fetch wind status for Ratnapura.
    Returns a dictionary with wind speed.
    """
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
    """
    Function to fetch sunrise and sunset times for Ratnapura.
    Returns a dictionary with sunrise and sunset times.
    """
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

def get_timestamp():
    """
    Function to fetch and return the current date and time.
    Returns a dictionary with the formatted date and time.
    """
    try:
        current_time = datetime.now().strftime('%d %b | %H:%M')
        result = {
            'datetime': current_time
        }
        if FLASK_AVAILABLE:
            current_app.logger.info(f"Timestamp: {json.dumps(result, indent=2)}")
        else:
            print(f"Timestamp: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching timestamp: {str(e)}")
        else:
            print(f"Error fetching timestamp: {str(e)}")
        return None

# def get_weather_background_video(weather_condition):
#     """
#     Function to determine the appropriate background video based on weather condition.
#     Returns the video filename for the current weather condition.
#     Uses available videos from the weather folder.
#     """
#     if not weather_condition:
#         if FLASK_AVAILABLE:
#             current_app.logger.info("No weather condition provided, using default video: videos/bg_vdo02.mp4")
#         else:
#             print("No weather condition provided, using default video: videos/bg_vdo02.mp4")
#         return 'videos/bg_vdo02.mp4'  # Default video
    
#     condition = weather_condition.lower()
#     if FLASK_AVAILABLE:
#         current_app.logger.info(f"Weather condition: '{condition}'")
#     else:
#         print(f"Weather condition: '{condition}'")
    
#     # Clear conditions - use sunny video
#     if condition in ['clear']:
#         return 'videos/weather/sunny.mp4'
    
#     # Partly Cloudy conditions - use partly_cloudy video
#     elif condition in ['partly cloudy']:
#         return 'videos/weather/partly_cloudy.mp4'
    
#     # Cloudy conditions - use cloudy video
#     elif condition in ['cloudy']:
#         return 'videos/weather/cloudy.mp4'
    
#     # Overcast conditions - use overcast video
#     elif condition in ['overcast']:
#         return 'videos/weather/overcast.mp4'
    
#     # Mist conditions - use mist video
#     elif condition in ['mist']:
#         return 'videos/weather/mist.mp4'
    
#     # Patchy Rain Possible - use patchy_rain video
#     elif condition in ['patchy rain possible']:
#         return 'videos/weather/patchy_rain.mp4'
    
#     # Patchy Light Drizzle - use patchy_llight_drizzle video (note the typo in filename)
#     elif condition in ['patchy light drizzle']:
#         return 'videos/weather/patchy_llight_drizzle.mp4'
    
#     # Light Drizzle - use light_rain video as closest match
#     elif condition in ['light drizzle']:
#         return 'videos/weather/light_rain.mp4'
    
#     # Patchy Light Rain - use light_rain video
#     elif condition in ['patchy light rain']:
#         return 'videos/weather/light_rain.mp4'
    
#     # Light Rain - use light_rain video
#     elif condition in ['light rain']:
#         return 'videos/weather/light_rain.mp4'
    
#     # Moderate Rain at Times - use moderate_rain_shower video
#     elif condition in ['moderate rain at times']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Moderate Rain - use moderate_rain_shower video
#     elif condition in ['moderate rain']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Heavy Rain at Times - use moderate_rain_shower video
#     elif condition in ['heavy rain at times']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Heavy Rain - use moderate_rain_shower video
#     elif condition in ['heavy rain']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Light Rain Shower - use light_rain video
#     elif condition in ['light rain shower']:
#         return 'videos/weather/light_rain.mp4'
    
#     # Moderate or Heavy Rain Shower - use moderate_rain_shower video
#     elif condition in ['moderate or heavy rain shower']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Torrential Rain Shower - use moderate_rain_shower video
#     elif condition in ['torrential rain shower']:
#         return 'videos/weather/moderate_rain_shower.mp4'
    
#     # Patchy Light Rain with Thunder - use thunderstorm video
#     elif condition in ['patchy light rain with thunder']:
#         return 'videos/weather/thunderstorm.mp4'
    
#     # Moderate or Heavy Rain with Thunder - use thunderstorm video
#     elif condition in ['moderate or heavy rain with thunder']:
#         return 'videos/weather/thunderstorm.mp4'
    
#     # Fallback patterns for similar conditions
#     elif any(word in condition for word in ['thunder', 'thunderstorm']):
#         return 'videos/weather/thunderstorm.mp4'
    
#     elif any(word in condition for word in ['rain', 'drizzle', 'shower']):
#         return 'videos/weather/patchy_rain.mp4'
    
#     elif any(word in condition for word in ['cloudy', 'overcast']):
#         return 'videos/weather/cloudy.mp4'
    
#     elif any(word in condition for word in ['mist', 'fog']):
#         return 'videos/weather/mist.mp4'
    
#     # Default fallback
#     else:
#         return 'videos/bg_vdo02.mp4'

def get_weather_background_video(weather_condition):
    """
    Simplified function to return bg_vdo01.mp4 as background video.
    This is a temporary solution until weather-specific videos are optimized.
    """
    if FLASK_AVAILABLE:
        current_app.logger.info("Using simplified background video: videos/bg_vdo01.mp4")
    else:
        print("Using simplified background video: videos/bg_vdo01.mp4")
    
    return 'videos/bg_vdo02.mp4'

def get_weather_icon(weather_condition):
    """
    Function to map weather conditions to FontAwesome icons.
    Returns the appropriate icon class for the weather condition.
    """
    if not weather_condition:
        return 'fas fa-question-circle'  # Default icon
    
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

def get_7day_overview():
    """
    Function to fetch and return 7-day overview data for Ratnapura.
    Includes 3 days of historical data, current day's data, and 3 days of forecast.
    Returns a list of dictionaries with date, max temp, min temp, and condition.
    """
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

        # Fetch 3 days of forecast data (free plan limit: 3 days max)
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
        
        # Get 2 days after current day (free plan only allows 3 days total)
        forecast_list = []
        for day in forecast_days[1:3]:  # This gives us tomorrow and day after tomorrow
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
        # Since we can't get more forecast data, we'll use current day data as placeholder
        placeholder_day = {
            'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'day_of_week': (datetime.now() + timedelta(days=3)).strftime('%A'),
            'max_temp_c': current_day['day']['maxtemp_c'],  # Use current day as reference
            'min_temp_c': current_day['day']['mintemp_c'],
            'condition': current_day['day']['condition']['text'],
            'icon': get_weather_icon(current_day['day']['condition']['text']),
            'precip_mm': 0.0
        }
        forecast_list.append(placeholder_day)

        # Combine history, current, and forecast
        overview_list = history_list + [current_entry] + forecast_list
        
        # Debug: Check the count
        if FLASK_AVAILABLE:
            current_app.logger.info(f"7-Day Overview - History: {len(history_list)}, Current: 1, Forecast: {len(forecast_list)}, Total: {len(overview_list)}")
            current_app.logger.info(f"7-Day Overview: {json.dumps(overview_list, indent=2)}")
        else:
            print(f"7-Day Overview - History: {len(history_list)}, Current: 1, Forecast: {len(forecast_list)}, Total: {len(overview_list)}")
            print(f"7-Day Overview: {json.dumps(overview_list, indent=2)}")
        return overview_list
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error fetching 7-day overview: {str(e)}")
        else:
            print(f"Error fetching 7-day overview: {str(e)}")
        return []