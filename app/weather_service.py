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
        
        # Get river height prediction using Gemini AI
        try:
            from .river_prediction_service import predict_river_height_trend
            
            # Get current river data for prediction
            river_data = {
                'river_name': current_river,
                'dam_name': 'Unknown',  # Will be updated by river service
                'current_height': 0.0,  # Will be updated by river service
                'observation_time': 'Unknown',
                'observation_date': 'Unknown'
            }
            
            # Try to get actual river data
            try:
                from .river import get_current_river_height
                actual_river_data = get_current_river_height()
                if actual_river_data:
                    river_data.update(actual_river_data)
            except:
                pass  # Use default values if river data unavailable
            
            # Create weather data for prediction
            weather_data_for_prediction = {
                'location': location['name'],
                'temperature_c': current['temp_c'],
                'condition': current['condition']['text'],
                'humidity': current.get('humidity', 0),
                'precip_mm': current.get('precip_mm', 0),
                'pressure_mb': current.get('pressure_mb', 0),
                'wind_kph': current.get('wind_kph', 0),
                'wind_dir': current.get('wind_dir', 'Unknown'),
                'uv': current.get('uv', 0),
                'visibility_km': current.get('vis_km', 0)
            }
            
            # Get river height prediction
            prediction = predict_river_height_trend(weather_data_for_prediction, river_data)
            
            if prediction and prediction.get('trend') != 'UNKNOWN':
                # Create 2-line description for UI
                trend = prediction.get('trend', 'SAME')
                confidence = prediction.get('confidence', 0)
                magnitude = prediction.get('magnitude', 'LOW')
                
                # First line: River height prediction
                line1 = f"River Height: {trend} ({magnitude} confidence: {confidence}%)"
                
                # Second line: Key reasoning
                reasoning = prediction.get('reasoning', [])
                if reasoning:
                    line2 = reasoning[0] if len(reasoning) > 0 else f"Current conditions: {current['condition']['text']}"
                else:
                    line2 = f"Current conditions: {current['condition']['text']}"
                
                prediction_description = f"{line1}\n{line2}"
                
                # Store full detailed description in notification database
                try:
                    from .notification_service import store_weather_notification
                    
                    # Create full description with all details
                    full_description = f"""River Height Prediction Analysis:

TREND: {trend} ({magnitude} confidence: {confidence}%)
TIMEFRAME: {prediction.get('timeframe', '6-12 hours')}
RISK ASSESSMENT: {prediction.get('risk_assessment', 'UNKNOWN')}

DETAILED DESCRIPTION:
{prediction.get('description', 'No detailed description available')}

REASONING:
{chr(10).join(f"• {reason}" for reason in reasoning) if reasoning else "• No specific reasoning provided"}

RECOMMENDATIONS:
{chr(10).join(f"• {rec}" for rec in prediction.get('recommendations', [])) if prediction.get('recommendations') else "• Monitor conditions regularly"}

WEATHER CONDITIONS:
• Location: {location['name']}
• Temperature: {current['temp_c']}°C
• Condition: {current['condition']['text']}
• Humidity: {current.get('humidity', 0)}%
• Precipitation: {current.get('precip_mm', 0)}mm
• Pressure: {current.get('pressure_mb', 0)}mb
• Wind: {current.get('wind_kph', 0)}km/h {current.get('wind_dir', 'Unknown')}

RIVER DATA:
• River: {current_river}
• Dam: {river_data.get('dam_name', 'Unknown')}
• Current Height: {river_data.get('current_height', 0)}m
• Observation: {river_data.get('observation_time', 'Unknown')} {river_data.get('observation_date', 'Unknown')}

PREDICTION TIMESTAMP: {prediction.get('prediction_timestamp', 'Unknown')}"""
                    
                    # Store in notification database
                    store_weather_notification(
                        location=location['name'],
                        river_name=current_river,
                        short_description=prediction_description,
                        full_description=full_description,
                        prediction_data=prediction,
                        weather_data=weather_data_for_prediction,
                        river_data=river_data
                    )
                    
                except Exception as e:
                    if FLASK_AVAILABLE:
                        try:
                            current_app.logger.warning(f"Error storing notification: {e}")
                        except:
                            print(f"Error storing notification: {e}")
                    else:
                        print(f"Error storing notification: {e}")
            else:
                prediction_description = f"Weather conditions for {location['name']}.\nCurrent conditions: {current['condition']['text']}."
                
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error in river prediction: {e}")
                except:
                    print(f"Error in river prediction: {e}")
            else:
                print(f"Error in river prediction: {e}")
            
            # Fallback to simple description
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
            'timestamp': datetime.now(pytz.timezone('Asia/Manila')),
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
    Function to fetch wind status for current location.
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
    Function to fetch sunrise and sunset times for current location.
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
    Function to fetch and return 7-day overview data for current location.
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