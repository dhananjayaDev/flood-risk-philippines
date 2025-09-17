"""
River Data Collector for Flask App
Automatically collects data from all 6 rivers every 30 minutes
Starts when Flask app initializes
"""

from app.multi_river_collector import (
    start_multi_river_collection, 
    stop_multi_river_collection,
    collect_all_rivers_now,
    get_multi_river_status
)

# Wrapper functions for multi-river collection
def start_river_data_collection(app):
    """Start automatic multi-river data collection"""
    return start_multi_river_collection(app)

def stop_river_data_collection():
    """Stop automatic multi-river data collection"""
    return stop_multi_river_collection()

def collect_data_now():
    """Manually collect data from all rivers now"""
    return collect_all_rivers_now()

def get_collection_status():
    """Get multi-river collection status"""
    return get_multi_river_status()
