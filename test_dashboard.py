#!/usr/bin/env python3
"""
Test script to verify the dashboard functionality
"""

import requests
import json
from datetime import datetime

def test_dashboard():
    """Test the dashboard endpoint"""
    try:
        # Test the home page (should redirect to login if not authenticated)
        response = requests.get('http://localhost:5000/home', timeout=10)
        print(f"Dashboard Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            
            # Check if key elements are present in the HTML
            html_content = response.text
            
            # Check for key dashboard elements
            checks = [
                ("Hero Section", "Welcome," in html_content),
                ("Stats Cards", "Active Sensors" in html_content),
                ("Map Panel", "flood-risk-map" in html_content),
                ("Charts Panel", "sensor-chart" in html_content),
                ("Alerts Panel", "Recent Alerts" in html_content),
                ("Notifications Panel", "Recent Notifications" in html_content),
                ("Leaflet.js", "leaflet" in html_content),
                ("Chart.js", "chart.js" in html_content),
                ("Socket.IO", "socket.io" in html_content)
            ]
            
            print("\n📊 Dashboard Component Check:")
            for component, present in checks:
                status = "✅" if present else "❌"
                print(f"  {status} {component}")
            
            # Check for dynamic data
            if "data.stats.active_sensors" in html_content:
                print("✅ Dynamic data integration working")
            
            print(f"\n📄 Dashboard HTML size: {len(html_content)} characters")
            
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the Flask application")
        print("   Make sure the app is running with: python app.py")
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

if __name__ == "__main__":
    print("🧪 Testing Flood Risk Dashboard")
    print("=" * 40)
    test_dashboard()
