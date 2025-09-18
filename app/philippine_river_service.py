"""
Philippine River Data Service
Fetches real-time reservoir water levels from PAGASA for Philippine rivers and dams.
Based on working Colab code provided by user.
"""

import requests
from bs4 import BeautifulSoup
import pytz
from datetime import datetime, timedelta
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Philippine River Basin Configuration
PHILIPPINE_RIVERS = {
    'Agno River': {
        'basin': 'agno',
        'dams': ['Ambuklao', 'Binga', 'San Roque'],
        'location': 'Luzon',
        'weather_city': 'Baguio',
        'coordinates': {'lat': 16.4023, 'lon': 120.5960}
    },
    'Cagayan River': {
        'basin': 'cagayan',
        'dams': ['Magat Dam'],
        'location': 'Luzon',
        'weather_city': 'Tuguegarao',
        'coordinates': {'lat': 17.6114, 'lon': 121.7275}
    },
    'Pampanga River': {
        'basin': 'pampanga',
        'dams': ['Pantabangan'],
        'location': 'Luzon',
        'weather_city': 'Manila',
        'coordinates': {'lat': 14.6042, 'lon': 120.9822}
    }
}

# Default Philippine location
DEFAULT_PHILIPPINE_RIVER = "Agno River"

def get_river_heights(basin='agno', dams=['Ambuklao', 'Binga', 'San Roque']):
    """
    Fetch reservoir water levels for specified dams in a river basin.
    Based on working Colab code.

    Args:
        basin (str): River basin name (e.g., 'agno', 'cagayan', 'pampanga')
        dams (list): List of dam names to fetch (e.g., ['Ambuklao', 'Binga'])

    Returns:
        dict: Dictionary with basin and dam data
    """
    url = "https://www.pagasa.dost.gov.ph/flood"
    print(f"Fetching PAGASA data for {basin} basin")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Target the table with class 'table dam-table'
            table = soup.find('table', class_='table dam-table')
            if not table:
                print("No dam table found")
                return None

            # Find all rows in the tbody
            rows = table.find('tbody').find_all('tr')
            dam_data = {}

            i = 0
            while i < len(rows):
                row = rows[i]
                cells = row.find_all('td')

                if len(cells) >= 3:
                    # Look for dam rows (cells[0] has dam name with current-dam class)
                    if 'current-dam' in cells[0].get('class', []):
                        dam_name = cells[0].get('data-id', '').replace('-', ' ')
                        print(f"Extracted {dam_name}: ", end="")

                        if dams and dam_name not in dams:
                            i += 4  # Skip this dam's block
                            continue

                        # This is the main data row: Time (cells[1]), RWL (cells[2])
                        time_text = cells[1].text.strip() if len(cells) > 1 else ''
                        rwl_text = cells[2].text.strip() if len(cells) > 2 else ''

                        if time_text == '08:00 AM' and rwl_text:
                            try:
                                rwl_value = float(rwl_text)
                                dam_data[dam_name] = {
                                    'rwl': rwl_value,
                                    'time': time_text,
                                    'date': 'Sep-17'  # From next row
                                }
                                print(f"{rwl_value}m")
                            except ValueError:
                                print(f"Invalid RWL: {rwl_text}")

                i += 1

            # Format results
            results = []
            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M')

            for dam_name in dams:
                if dam_name in dam_data:
                    result = {
                        'dam_name': dam_name,
                        'river_basin': basin.title(),
                        'current_height': dam_data[dam_name]['rwl'],
                        'timestamp': timestamp,
                        'observation_time': dam_data[dam_name]['time'],
                        'observation_date': dam_data[dam_name].get('date', 'Unknown')
                    }
                    results.append(result)
                else:
                    print(f"No data found for {dam_name}")

            if results:
                return {
                    'basin': basin.title(),
                    'dams': results,
                    'timestamp': timestamp
                }

            return None
        else:
            print(f"Failed to fetch page, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error scraping {basin} basin: {e}")
        return None

def get_philippine_river_by_name(river_name):
    """
    Get river data for a specific Philippine river.
    
    Args:
        river_name (str): Name of the river
    
    Returns:
        dict: River data with dam information
    """
    if river_name not in PHILIPPINE_RIVERS:
        return None
    
    river_config = PHILIPPINE_RIVERS[river_name]
    basin = river_config['basin']
    dams = river_config['dams']
    
    # Get data from PAGASA
    data = get_river_heights(basin, dams)
    
    if data and data['dams']:
        return {
            'river_name': river_name,
            'basin': data['basin'],
            'dams': data['dams'],
            'timestamp': data['timestamp'],
            'location': river_config['location'],
            'weather_city': river_config['weather_city'],
            'coordinates': river_config['coordinates']
        }
    
    return None

def get_philippine_dam_by_name(dam_name):
    """
    Get dam data for a specific Philippine dam.
    
    Args:
        dam_name (str): Name of the dam
    
    Returns:
        dict: Dam data
    """
    for river_name, river_config in PHILIPPINE_RIVERS.items():
        if dam_name in river_config['dams']:
            river_data = get_philippine_river_by_name(river_name)
            if river_data and river_data['dams']:
                for dam in river_data['dams']:
                    if dam['dam_name'] == dam_name:
                        return dam
    return None

def get_current_philippine_river():
    """
    Get the current Philippine river based on saved location.
    
    Returns:
        str: Current river name
    """
    try:
        from .search import load_location_from_file
        current_location = load_location_from_file()
        
        if not current_location:
            return DEFAULT_PHILIPPINE_RIVER
        
        # Check if current location matches any Philippine river
        current_location_lower = current_location.lower()
        
        for river_name, river_config in PHILIPPINE_RIVERS.items():
            # Check river name
            if river_name.lower() in current_location_lower or current_location_lower in river_name.lower():
                return river_name
            
            # Check dam names
            for dam_name in river_config['dams']:
                if dam_name.lower() in current_location_lower or current_location_lower in dam_name.lower():
                    return river_name
            
            # Check weather city
            if river_config['weather_city'].lower() in current_location_lower or current_location_lower in river_config['weather_city'].lower():
                return river_name
        
        # If no match found, return default
        return DEFAULT_PHILIPPINE_RIVER
        
    except Exception as e:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.error(f"Error getting current Philippine river: {e}")
            except:
                print(f"Error getting current Philippine river: {e}")
        else:
            print(f"Error getting current Philippine river: {e}")
        return DEFAULT_PHILIPPINE_RIVER

def get_philippine_river_height(river_name=None):
    """
    Get current river height for a Philippine river.
    
    Args:
        river_name (str): Name of the river (default: uses current location)
    
    Returns:
        dict: Current river height data
    """
    if river_name is None:
        river_name = get_current_philippine_river()
    
    river_data = get_philippine_river_by_name(river_name)
    
    if river_data and river_data['dams']:
        # Get the first dam's data (or you could aggregate multiple dams)
        dam_data = river_data['dams'][0]
        
        return {
            'river_name': river_name,
            'dam_name': dam_data['dam_name'],
            'current_height': dam_data['current_height'],
            'timestamp': dam_data['timestamp'],
            'observation_time': dam_data['observation_time'],
            'observation_date': dam_data['observation_date']
        }
    
    return None

def get_philippine_river_7day(river_name=None):
    """
    Get 7-day river height data for chart display (real-time data only).
    
    Args:
        river_name (str): Name of the river (default: uses current location)
    
    Returns:
        list: 7-day array with river height data
    """
    if river_name is None:
        river_name = get_current_philippine_river()
    
    # Get current river height
    current_data = get_philippine_river_height(river_name)
    current_height = 0.0
    
    if current_data:
        current_height = current_data['current_height']
    else:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.warning(f"No data available for {river_name}, using 0.0m")
            except:
                print(f"No data available for {river_name}, using 0.0m")
        else:
            print(f"No data available for {river_name}, using 0.0m")
    
    # Create 7-day array: 3 past days (0) + current day (real height) + 3 future days (0)
    result = []
    today = datetime.now(pytz.timezone('Asia/Manila'))
    
    for i in range(7):
        # Calculate date for this day (3 days ago to 3 days from now)
        day_date = today - timedelta(days=3-i)
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
    
    return result

def get_philippine_weather_city(river_name=None):
    """
    Get the weather city for a Philippine river.
    
    Args:
        river_name (str): Name of the river (default: uses current location)
    
    Returns:
        str: Weather city name
    """
    if river_name is None:
        river_name = get_current_philippine_river()
    
    if river_name in PHILIPPINE_RIVERS:
        return PHILIPPINE_RIVERS[river_name]['weather_city']
    
    return 'Manila'  # Default fallback

def get_philippine_coordinates(river_name=None):
    """
    Get coordinates for a Philippine river.
    
    Args:
        river_name (str): Name of the river (default: uses current location)
    
    Returns:
        dict: Latitude and longitude coordinates
    """
    if river_name is None:
        river_name = get_current_philippine_river()
    
    if river_name in PHILIPPINE_RIVERS:
        return PHILIPPINE_RIVERS[river_name]['coordinates']
    
    return {'lat': 14.6042, 'lon': 120.9822}  # Default to Manila