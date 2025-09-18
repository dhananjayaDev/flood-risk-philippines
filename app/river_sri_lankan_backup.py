import requests
import pandas as pd
import time
from datetime import datetime
import pytz
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Global river configuration
# SRI LANKAN RIVERS - COMMENTED OUT FOR PHILIPPINE FOCUS
# DEFAULT_RIVER = "Kalu Ganga (Ratnapura)"
DEFAULT_RIVER = "Agno River"  # Philippine default

def get_current_river():
    """
    Check current_location.txt and return the appropriate river name.
    Now focuses on Philippine rivers only.
    """
    try:
        # Get the current location from the file
        from .search import load_location_from_file
        current_location = load_location_from_file()
        
        if not current_location:
            return DEFAULT_RIVER
        
        # Check if current location matches any Philippine river
        try:
            from .philippine_river_service import get_current_philippine_river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                return philippine_river
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river: {e}")
                except:
                    print(f"Error checking Philippine river: {e}")
            else:
                print(f"Error checking Philippine river: {e}")
        
        # SRI LANKAN RIVER LOGIC - COMMENTED OUT
        # Check if current location matches any available river
        # for river_name in RIVER_API_KEYS.keys():
        #     # Extract location from river name (e.g., "Kuru Ganga (Kuruvita)" -> "Kuruvita")
        #     river_location = river_name.split('(')[-1].split(')')[0].strip().lower()
        #     current_location_lower = current_location.lower()
        #     
        #     # Check if current location matches the river location
        #     if (current_location_lower in river_location or 
        #         river_location in current_location_lower or
        #         current_location_lower in river_name.lower() or 
        #         river_name.lower() in current_location_lower):
        #         return river_name
                
        # If no match found, return default
        return DEFAULT_RIVER
        
    except Exception as e:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.error(f"Error getting current river: {e}")
            except:
                print(f"Error getting current river: {e}")
        else:
            print(f"Error getting current river: {e}")
        return DEFAULT_RIVER

# SRI LANKAN RIVER API ENDPOINTS - COMMENTED OUT FOR PHILIPPINE FOCUS
# Working API endpoints for river level data
# RIVER_API_KEYS = {
#     "Kalu Ganga (Ratnapura)": "2bq292rf6uz",
#     "Kuru Ganga (Kuruvita)": "76k6cqo0ipwk", 
#     "Galathura Oya (Ayagama)": "6nb2troqa5c0",
#     "Denawaka Ganga (Pelmadulla)": "1kp1hhh7zbu",
#     "Kukule Ganga (Kalawana)": "5asknpp28bs",
#     "Wey Ganga (Kahawaththa)": "5f4al4atv8ws",
#     "Niriella Ganga (Elapatha)": "2q6uiwmovjcw"
# }

# SRI LANKAN API FUNCTIONS - COMMENTED OUT FOR PHILIPPINE FOCUS
# def get_api_urls():
#     """
#     Generate API URLs for the last 24 hours using current time.
#     Returns dictionary with river names and their corresponding API URLs.
#     """
#     # Current time in Asia/Colombo timezone
#     current_time = datetime.now(pytz.timezone('Asia/Colombo'))
#     
#     # Calculate timestamps for last 24 hours (in milliseconds)
#     end_time_ms = int(current_time.timestamp() * 1000)
#     start_time_ms = int((current_time - pd.Timedelta(hours=24)).timestamp() * 1000)
#     
#     river_urls = {}
#     for river_name, api_key in RIVER_API_KEYS.items():
#         title_url = f"https://api.rivernet.lk/api/reports/river-level/title/minute/{start_time_ms}/{end_time_ms}?keys={api_key}"
#         river_urls[river_name] = title_url
#     
#     return river_urls

# SRI LANKAN API HELPER - COMMENTED OUT FOR PHILIPPINE FOCUS
# def fetch_api(url):
#     """
#     Helper function to make API requests.
#     """
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             raise Exception(f"API request failed: Status code {response.status_code}")
#     except Exception as e:
#         if FLASK_AVAILABLE:
#             current_app.logger.error(f"Error fetching API: {str(e)}")
#         else:
#             print(f"Error fetching API: {str(e)}")
#         return None

# SRI LANKAN RIVER LEVELS FUNCTION - COMMENTED OUT FOR PHILIPPINE FOCUS
# def get_river_levels(river_name=None):
#     """
#     Fetch and return river level data for a specific river using working API endpoints.
#     Args:
#         river_name (str): Name of the river (default: uses current location to determine river)
#     Returns:
#         pandas.DataFrame: DataFrame with timestamp, river_level, and river columns,
#                          or None if no data is retrieved.
#     """
    try:
        # Use current location-based river if no river name provided
        if river_name is None:
            river_name = get_current_river()
        
        # Get API URLs for all rivers
        river_urls = get_api_urls()
        
        if river_name not in river_urls:
            if FLASK_AVAILABLE:
                current_app.logger.error(f"River '{river_name}' not found in available rivers")
            else:
                print(f"River '{river_name}' not found in available rivers")
            return None
        
        title_url = river_urls[river_name]
        chart_url = title_url.replace("/title/", "/chart/")
        
        all_data = []
        
        # Try chart endpoint first
        try:
            chart_data = fetch_api(chart_url)
            if chart_data and "results" in chart_data and "series" in chart_data["results"] and len(chart_data["results"]["series"]) > 0 and "data" in chart_data["results"]["series"][0]:
                # Parse chart data correctly - data comes as list of dicts with 'x' and 'y' keys
                chart_series = chart_data["results"]["series"][0]["data"]
                records = []
                for point in chart_series:
                    records.append({
                        "timestamp": pd.to_datetime(point["x"], unit="ms", utc=True).tz_convert('Asia/Colombo'),
                        "river_level": float(point["y"]),
                        "river": river_name
                    })
                df = pd.DataFrame(records)
                all_data.append(df)
                if FLASK_AVAILABLE:
                    current_app.logger.info(f"Chart data retrieved for {river_name}")
                else:
                    print(f"Chart data retrieved for {river_name}")
            else:
                if FLASK_AVAILABLE:
                    current_app.logger.info(f"No series data in chart response for {river_name}, trying title endpoint")
                else:
                    print(f"No series data in chart response for {river_name}, trying title endpoint")
                
                # Fall back to title endpoint
                title_data = fetch_api(title_url)
                if title_data and "results" in title_data and "deviceData" in title_data["results"] and title_data["results"]["deviceData"]:
                    device_data = title_data["results"]["deviceData"][0]
                    records = []
                    
                    if "latestRecord" in device_data:
                        latest = device_data["latestRecord"]
                        records.append({
                            "timestamp": pd.to_datetime(latest["datetime"], format='mixed', errors='coerce', utc=True).tz_convert('Asia/Colombo'),
                            "river_level": float(latest["value"]),
                            "river": river_name
                        })
                    
                    if "latest" in device_data and "before30mLevel" in device_data["latest"]:
                        before30m = device_data["latest"]["before30mLevel"]
                        records.append({
                            "timestamp": pd.to_datetime(before30m["datetime"], format='mixed', errors='coerce', utc=True).tz_convert('Asia/Colombo'),
                            "river_level": float(before30m["value"]),
                            "river": river_name
                        })
                    
                    if records:
                        df = pd.DataFrame(records)
                        all_data.append(df)
                        if FLASK_AVAILABLE:
                            current_app.logger.info(f"Title data retrieved for {river_name}")
                        else:
                            print(f"Title data retrieved for {river_name}")
                    else:
                        if FLASK_AVAILABLE:
                            current_app.logger.warning(f"No valid data in title response for {river_name}")
                        else:
                            print(f"No valid data in title response for {river_name}")
        except Exception as e:
            if FLASK_AVAILABLE:
                current_app.logger.error(f"Error processing {chart_url}: {str(e)}")
            else:
                print(f"Error processing {chart_url}: {str(e)}")
        
        time.sleep(0.5)  # Rate limiting

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=["timestamp", "river"])
            if FLASK_AVAILABLE:
                current_app.logger.info(f"River level data retrieved for {river_name}: {len(combined_df)} records")
            else:
                print(f"\nRiver level data for {river_name}:")
                print(combined_df[["river", "timestamp", "river_level"]].head())
            return combined_df
        else:
            if FLASK_AVAILABLE:
                current_app.logger.warning(f"No data available for {river_name}")
            else:
                print(f"No data available for {river_name}")
            return None
            
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error getting river levels for {river_name}: {str(e)}")
        else:
            print(f"Error getting river levels for {river_name}: {str(e)}")
        return None

def get_current_river_height(river_name=None):
    """
    Get the current river height for a specific river using working API endpoints.
    Args:
        river_name (str): Name of the river (default: uses current location to determine river)
    Returns:
        dict: Dictionary with current river height data or None if no data
    """
    try:
        # Use current location-based river if no river name provided
        if river_name is None:
            river_name = get_current_river()
        
        # Check if this is a Philippine river
        try:
            from .philippine_river_service import get_philippine_river_height, get_current_philippine_river
            
            # Check if current river is a Philippine river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                philippine_data = get_philippine_river_height(philippine_river)
                if philippine_data:
                    return philippine_data
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river: {e}")
                except:
                    print(f"Error checking Philippine river: {e}")
            else:
                print(f"Error checking Philippine river: {e}")
            
        # If not Philippine, use Sri Lankan river system
        df = get_river_levels(river_name)
        
        if df is not None and not df.empty:
            # Get the latest record for the specified river
            latest_data = df[df['river'] == river_name].sort_values('timestamp').tail(1)
            
            if not latest_data.empty:
                current_height = latest_data['river_level'].iloc[0]
                timestamp = latest_data['timestamp'].iloc[0]
                
                result = {
                    'river_name': river_name,
                    'current_height': float(current_height),
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M'),
                    'date': timestamp.strftime('%Y-%m-%d'),
                    'time': timestamp.strftime('%H:%M')
                }
                
                if FLASK_AVAILABLE:
                    current_app.logger.info(f"Current {river_name} height: {current_height}m at {timestamp}")
                else:
                    print(f"Current {river_name} height: {current_height}m at {timestamp}")
                
                return result
        
        if FLASK_AVAILABLE:
            current_app.logger.warning(f"No current data available for {river_name}")
        else:
            print(f"No current data available for {river_name}")
        return None
        
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error getting current river height: {str(e)}")
        else:
            print(f"Error getting current river height: {str(e)}")
        return None

def get_river_height_7day(river_name=None):
    """
    Get 7-day river height data for chart display.
    Previous days and future days show 0 (no data), current day shows actual height.
    Args:
        river_name (str): Name of the river (default: uses current location to determine river)
    Returns:
        list: 7-day array with river height data
    """
    try:
        # Use current location-based river if no river name provided
        if river_name is None:
            river_name = get_current_river()
        
        # Check if this is a Philippine river
        try:
            from .philippine_river_service import get_philippine_river_7day, get_current_philippine_river
            
            # Check if current river is a Philippine river
            philippine_river = get_current_philippine_river()
            if philippine_river != 'Agno River':  # Default, means we found a match
                philippine_data = get_philippine_river_7day(philippine_river)
                if philippine_data:
                    return philippine_data
        except Exception as e:
            if FLASK_AVAILABLE:
                try:
                    current_app.logger.warning(f"Error checking Philippine river 7-day: {e}")
                except:
                    print(f"Error checking Philippine river 7-day: {e}")
            else:
                print(f"Error checking Philippine river 7-day: {e}")
            
        # If not Philippine, use Sri Lankan river system
        # Get current river height using working API
        current_data = get_current_river_height(river_name)
        current_height = 0.0
        
        if current_data:
            current_height = current_data['current_height']
            if FLASK_AVAILABLE:
                current_app.logger.info(f"Current {river_name} height: {current_height}m")
            else:
                print(f"Current {river_name} height: {current_height}m")
        else:
            # No fallback data - use 0 if no real data available
            current_height = 0.0
            if FLASK_AVAILABLE:
                current_app.logger.warning(f"No data available for {river_name}, using 0.0m")
            else:
                print(f"No data available for {river_name}, using 0.0m")
        
        # Create 7-day array: 3 past days (0) + current day (real height) + 3 future days (0)
        result = []
        today = datetime.now(pytz.timezone('Asia/Colombo'))
        
        for i in range(7):
            # Calculate date for this day (3 days ago to 3 days from now)
            day_date = today - pd.Timedelta(days=3-i)
            day_name = day_date.strftime('%a')  # Dynamic day name (Mon, Tue, Wed, etc.)
            
            # Only current day (i=3) gets real height, others get 0
            if i == 3:  # Current day
                height = current_height
            else:
                height = 0.0  # Past and future days
            
            result.append({
                'day': day_name,
                'height': height,
                'date': day_date.strftime('%Y-%m-%d'),
                'is_current': i == 3
            })
        
        if FLASK_AVAILABLE:
            current_app.logger.info(f"7-day river height data for {river_name}: {len(result)} days")
        else:
            print(f"7-day river height data for {river_name}: {len(result)} days")
        
        return result
        
    except Exception as e:
        if FLASK_AVAILABLE:
            current_app.logger.error(f"Error getting 7-day river height: {str(e)}")
        else:
            print(f"Error getting 7-day river height: {str(e)}")
        
        # Return empty data on error (no fallback)
        result = []
        today = datetime.now(pytz.timezone('Asia/Colombo'))
        for i in range(7):
            day_date = today - pd.Timedelta(days=3-i)
            day_name = day_date.strftime('%a')  # Dynamic day name
            result.append({
                'day': day_name,
                'height': 0.0,  # Always 0 on error
                'date': day_date.strftime('%Y-%m-%d'),
                'is_current': i == 3
            })
        return result

if __name__ == "__main__":
    # Test with default river (Kalu Ganga (Ratnapura))
    df = get_river_levels()
    if df is not None:
        print(df[["river", "timestamp", "river_level"]])
    
    # Test current height
    current = get_current_river_height()
    if current:
        print(f"\nCurrent height: {current}")
    
    # Test 7-day data
    seven_day = get_river_height_7day()
    if seven_day:
        print(f"\n7-day data: {seven_day}")