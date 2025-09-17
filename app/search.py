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
        return 'Ratnapura'  # Default location
    except Exception as e:
        print(f"Error loading location from file: {e}")
        return 'Ratnapura'

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
    Simple search function that updates weather location.
    
    Args:
        search_term (str): User's search input
    
    Returns:
        dict: Search result
    """
    return update_weather_location(search_term)

def get_available_locations():
    """
    Get list of available locations for search suggestions.
    
    Returns:
        list: List of available location names
    """
    return [
        'Ratnapura', 'Colombo', 'Kandy', 'Galle', 'Jaffna',
        'Kalu Ganga (Ratnapura)', 'Kuru Ganga (Kuruvita)', 
        'Galathura Oya (Ayagama)', 'Denawaka Ganga (Pelmadulla)',
        'Kukule Ganga (Kalawana)', 'Wey Ganga (Kahawaththa)',
        'Niriella Ganga (Elapatha)'
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