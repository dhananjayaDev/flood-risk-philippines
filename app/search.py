import requests
import json
import os
from datetime import datetime, timedelta
try:
    from flask import current_app, session
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# File to store the current location
LOCATION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'current_location.txt')

def save_location_to_file(location):
    """Save location to file for persistence across page reloads."""
    try:
        print(f"DEBUG: Saving location '{location}' to file: {LOCATION_FILE}")
        with open(LOCATION_FILE, 'w') as f:
            f.write(location)
        print(f"DEBUG: Successfully saved location to file")
        return True
    except Exception as e:
        print(f"Error saving location to file: {e}")
        print(f"DEBUG: File path was: {LOCATION_FILE}")
        return False

def load_location_from_file():
    """Load location from file."""
    try:
        if os.path.exists(LOCATION_FILE):
            with open(LOCATION_FILE, 'r', encoding='utf-8-sig') as f:
                return f.read().strip()
        return 'Agno River'  # Default Philippine location
    except Exception as e:
        print(f"Error loading location from file: {e}")
        return 'Agno River'

def update_weather_location(search_term):
    """
    Update the weather service location based on user input.
    
    Args:
        search_term (str): User's search input
    
    Returns:
        dict: Result of the update operation
    """
    try:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.info(f"Updating weather location to: '{search_term}'")
            except:
                print(f"Updating weather location to: '{search_term}'")
        else:
            print(f"Updating weather location to: '{search_term}'")
        
        # Save location to file for persistence
        save_location_to_file(search_term)
        
        # Update weather service location
        from . import weather_service
        weather_service.set_location(search_term)
        
        return {
            'success': True,
            'location': search_term,
            'message': f'Weather location updated to {search_term}'
        }
        
    except Exception as e:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.error(f"Error updating weather location: {str(e)}")
            except:
                print(f"Error updating weather location: {str(e)}")
        else:
            print(f"Error updating weather location: {str(e)}")
        
        return {
            'success': False,
            'error': str(e)
        }

def search_location_data(search_term):
    """
    Enhanced search function that handles both Sri Lankan and Philippine locations.
    
    Args:
        search_term (str): User's search input
    
    Returns:
        dict: Search result
    """
    try:
        # Check if this is a Philippine location
        from .philippine_river_service import PHILIPPINE_RIVERS, get_philippine_river_by_name, get_philippine_dam_by_name
        
        search_lower = search_term.lower()
        
        # Check if search term matches any Philippine river
        for river_name, river_config in PHILIPPINE_RIVERS.items():
            if (search_lower in river_name.lower() or 
                river_name.lower() in search_lower or
                search_lower in river_config['weather_city'].lower() or
                river_config['weather_city'].lower() in search_lower):
                
                # Test if we can get data for this river
                river_data = get_philippine_river_by_name(river_name)
                if river_data:
                    # Save the location to file for persistence
                    save_location_to_file(search_term)
                    return {
                        'success': True,
                        'location': search_term,
                        'river_name': river_name,
                        'weather_city': river_config['weather_city'],
                        'coordinates': river_config['coordinates'],
                        'is_philippine': True,
                        'message': f'Switched to {river_name} (Philippines)'
                    }
        
        # Check if search term matches any Philippine dam
        for river_name, river_config in PHILIPPINE_RIVERS.items():
            for dam_name in river_config['dams']:
                if (search_lower in dam_name.lower() or 
                    dam_name.lower() in search_lower):
                    
                    # Test if we can get data for this dam
                    dam_data = get_philippine_dam_by_name(dam_name)
                    if dam_data:
                        # Save the location to file for persistence
                        save_location_to_file(search_term)
                        return {
                            'success': True,
                            'location': search_term,
                            'river_name': river_name,
                            'dam_name': dam_name,
                            'weather_city': river_config['weather_city'],
                            'coordinates': river_config['coordinates'],
                            'is_philippine': True,
                            'message': f'Switched to {dam_name} in {river_name} (Philippines)'
                        }
        
        # If not a Philippine location, use the original Sri Lankan search
        return update_weather_location(search_term)
        
    except Exception as e:
        if FLASK_AVAILABLE:
            try:
                current_app.logger.error(f"Error in enhanced search: {str(e)}")
            except:
                print(f"Error in enhanced search: {str(e)}")
        else:
            print(f"Error in enhanced search: {str(e)}")
        
        # Fallback to original search
        return update_weather_location(search_term)

def get_available_locations():
    """
    Get list of available locations for search suggestions.
    Now focuses on Philippine locations only.
    
    Returns:
        list: List of available location names
    """
    return [
        # Philippine locations (primary focus)
        'Agno River', 'Cagayan River', 'Pampanga River',
        'Ambuklao Dam', 'Binga Dam', 'San Roque Dam', 'Magat Dam',
        'Baguio', 'Tuguegarao', 'Manila', 'Luzon',
        
        # SRI LANKAN LOCATIONS - COMMENTED OUT FOR PHILIPPINE FOCUS
        # 'Ratnapura', 'Colombo', 'Kandy', 'Galle', 'Jaffna',
        # 'Kalu Ganga (Ratnapura)', 'Kuru Ganga (Kuruvita)', 
        # 'Galathura Oya (Ayagama)', 'Denawaka Ganga (Pelmadulla)',
        # 'Kukule Ganga (Kalawana)', 'Wey Ganga (Kahawaththa)',
        # 'Niriella Ganga (Elapatha)',
    ]

if __name__ == "__main__":
    # Test the search functionality
    test_terms = ["ratnapura", "kalu ganga", "colombo", "kandy", "kuru ganga"]
    
    for term in test_terms:
        print(f"\n{'='*50}")
        print(f"Testing search for: '{term}'")
        print(f"{'='*50}")
        
        result = search_location_data(term)
        if result['success']:
            print(f"Location: {result['location']}")
            print(f"River: {result['river']}")
        else:
            print(f"Search failed: {result['error']}")