"""
Upstream River Monitoring System
Monitors 5 critical upstream locations that affect Kalu Ganga at Ratnapura
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import pytz
from app import db
from app.models import RiverHeight

# Critical upstream locations affecting Kalu Ganga at Ratnapura
UPSTREAM_LOCATIONS = {
    "Kuru Ganga (Kuruvita)": {
        "api_key": "76k6cqo0ipwk",
        "priority": 1,  # Highest priority
        "description": "Major tributary - direct impact on Ratnapura"
    },
    "Kukule Ganga (Kalawana)": {
        "api_key": "5asknpp28bs", 
        "priority": 1,  # Highest priority - has reservoir
        "description": "Reservoir location - spillage causes sudden flooding"
    },
    "Galathura Oya (Ayagama)": {
        "api_key": "6nb2troqa5c0",
        "priority": 2,
        "description": "Eastern catchment - important tributary"
    },
    "Denawaka Ganga (Pelmadulla)": {
        "api_key": "1kp1hhh7zbu",
        "priority": 2,
        "description": "Northern catchment - significant water contribution"
    },
    "Wey Ganga (Kahawaththa)": {
        "api_key": "5f4al4atv8ws",
        "priority": 3,
        "description": "Southern catchment - affects water flow patterns"
    }
}

def get_upstream_api_urls():
    """
    Generate API URLs for upstream locations for the last 24 hours.
    """
    current_time = datetime.now(pytz.timezone('Asia/Colombo'))
    end_time_ms = int(current_time.timestamp() * 1000)
    start_time_ms = int((current_time - pd.Timedelta(hours=24)).timestamp() * 1000)
    
    upstream_urls = {}
    for location, config in UPSTREAM_LOCATIONS.items():
        api_key = config["api_key"]
        title_url = f"https://api.rivernet.lk/api/reports/river-level/title/minute/{start_time_ms}/{end_time_ms}?keys={api_key}"
        upstream_urls[location] = title_url
    
    return upstream_urls

def fetch_upstream_data(location_name, url):
    """
    Fetch river level data for a specific upstream location.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"API request failed for {location_name}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for {location_name}: {e}")
        return None

def process_upstream_data(location_name, data):
    """
    Process upstream river data and extract current height.
    """
    try:
        if not data or "results" not in data:
            return None
        
        results = data["results"]
        
        # Try to get latest record
        if "deviceData" in results and results["deviceData"]:
            device_data = results["deviceData"][0]
            
            if "latestRecord" in device_data:
                latest = device_data["latestRecord"]
                return {
                    "location": location_name,
                    "height": float(latest["value"]),
                    "timestamp": latest["datetime"],
                    "status": "current"
                }
        
        # Try to get chart data
        chart_url = url.replace("/title/", "/chart/")
        chart_data = fetch_upstream_data(location_name, chart_url)
        
        if chart_data and "results" in chart_data and "series" in chart_data["results"]:
            series = chart_data["results"]["series"]
            if series and len(series) > 0 and "data" in series[0]:
                chart_series = series[0]["data"]
                if chart_series:
                    latest_point = chart_series[-1]  # Get most recent point
                    return {
                        "location": location_name,
                        "height": float(latest_point["y"]),
                        "timestamp": pd.to_datetime(latest_point["x"], unit="ms", utc=True).tz_convert('Asia/Colombo').strftime('%Y-%m-%d %H:%M'),
                        "status": "current"
                    }
        
        return None
        
    except Exception as e:
        print(f"Error processing data for {location_name}: {e}")
        return None

def collect_all_upstream_data():
    """
    Collect river level data from all 5 critical upstream locations.
    """
    print("🌊 Collecting upstream river data...")
    
    upstream_urls = get_upstream_api_urls()
    upstream_data = []
    
    for location_name, url in upstream_urls.items():
        print(f"📡 Fetching data for {location_name}...")
        
        # Fetch data
        data = fetch_upstream_data(location_name, url)
        
        if data:
            # Process data
            processed = process_upstream_data(location_name, data)
            if processed:
                upstream_data.append(processed)
                print(f"✅ {location_name}: {processed['height']}m at {processed['timestamp']}")
            else:
                print(f"⚠️ {location_name}: No valid data found")
        else:
            print(f"❌ {location_name}: Failed to fetch data")
        
        # Rate limiting
        time.sleep(0.5)
    
    return upstream_data

def analyze_upstream_impact(upstream_data, ratnapura_height):
    """
    Analyze the impact of upstream locations on Ratnapura water level.
    """
    print("\n📊 Upstream Impact Analysis:")
    print(f"Ratnapura Current Height: {ratnapura_height}m")
    print("\nUpstream Locations:")
    
    for data in upstream_data:
        location = data['location']
        height = data['height']
        priority = UPSTREAM_LOCATIONS[location]['priority']
        description = UPSTREAM_LOCATIONS[location]['description']
        
        # Calculate potential impact
        if height > 3.0:  # High water level threshold
            impact_level = "🔴 HIGH IMPACT"
        elif height > 2.0:
            impact_level = "🟡 MEDIUM IMPACT"
        else:
            impact_level = "🟢 LOW IMPACT"
        
        print(f"  {location}: {height}m - {impact_level}")
        print(f"    Priority: {priority} - {description}")
    
    return upstream_data

def get_upstream_summary():
    """
    Get a summary of all upstream locations and their current status.
    """
    try:
        # Collect upstream data
        upstream_data = collect_all_upstream_data()
        
        # Get current Ratnapura height
        from app.river import get_current_river_height
        ratnapura_data = get_current_river_height("Kalu Ganga (Ratnapura)")
        ratnapura_height = ratnapura_data['current_height'] if ratnapura_data else 0.0
        
        # Analyze impact
        analysis = analyze_upstream_impact(upstream_data, ratnapura_height)
        
        return {
            "ratnapura_height": ratnapura_height,
            "upstream_locations": analysis,
            "collection_time": datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S'),
            "total_locations": len(analysis)
        }
        
    except Exception as e:
        print(f"Error in upstream monitoring: {e}")
        return None

if __name__ == "__main__":
    print("=== Upstream River Monitoring System ===")
    print("Monitoring 5 critical locations affecting Kalu Ganga at Ratnapura")
    
    summary = get_upstream_summary()
    
    if summary:
        print(f"\n✅ Monitoring complete!")
        print(f"📊 Collected data from {summary['total_locations']} upstream locations")
        print(f"⏰ Collection time: {summary['collection_time']}")
    else:
        print("❌ Monitoring failed!")
