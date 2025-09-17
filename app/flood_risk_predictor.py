"""
Flood Risk Prediction Module
Uses Gemini AI to predict flood risk for Ratnapura based on:
- River heights from all 6 rivers (Kalu Ganga, Kuru Ganga, Wey Ganga, Denawaka Ganga, Kukule Ganga, Galathura Oya)
- Weather conditions from all 6 locations (Pelmadulla, Ratnapura, Kalawana, Kuruvita, Ayagama, Kahawatta)
"""

import google.generativeai as genai
import json
from datetime import datetime, timedelta
import pytz
from app import db
from app.models import (
    RiverHeight, KuruGangaHeight, WeyGangaHeight, DenawakaGangaHeight, 
    KukuleGangaHeight, GalathuraOyaHeight,
    PelmadullaWeather, RatnapuraWeather, KalawanaWeather,
    KuruvitaWeather, AyagamaWeather, KahawattaWeather
)

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyDpZPw0ea0lkXG5DK7dT1ToEImjDm31rgA"
genai.configure(api_key=GEMINI_API_KEY)

class FloodRiskPredictor:
    """Flood risk prediction using Gemini AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.risk_levels = {
            'LOW': {'level': 1, 'color': 'green', 'description': 'Minimal flood risk'},
            'MODERATE': {'level': 2, 'color': 'yellow', 'description': 'Moderate flood risk - monitor closely'},
            'HIGH': {'level': 3, 'color': 'orange', 'description': 'High flood risk - prepare for flooding'},
            'CRITICAL': {'level': 4, 'color': 'red', 'description': 'Critical flood risk - immediate action required'}
        }
    
    def get_river_data(self, hours_back=24):
        """Get river height data from all rivers for the last N hours"""
        end_time = datetime.now(pytz.timezone('Asia/Colombo'))
        start_time = end_time - timedelta(hours=hours_back)
        
        river_data = {}
        
        # River models and their names
        river_models = [
            (RiverHeight, 'Kalu Ganga (Ratnapura)', 'kalugangadb'),
            (KuruGangaHeight, 'Kuru Ganga (Kuruvita)', 'kuruganga'),
            (WeyGangaHeight, 'Wey Ganga (Kalawana)', 'weyganga'),
            (DenawakaGangaHeight, 'Denawaka Ganga (Pelmadulla)', 'denawakaganga'),
            (KukuleGangaHeight, 'Kukule Ganga (Kahawatta)', 'kukuleganga'),
            (GalathuraOyaHeight, 'Galathura Oya (Ayagama)', 'galathuraoya')
        ]
        
        for model_class, river_name, bind_key in river_models:
            try:
                # Get recent data
                recent_data = model_class.query.filter(
                    model_class.timestamp >= start_time,
                    model_class.timestamp <= end_time
                ).order_by(model_class.timestamp.desc()).limit(10).all()
                
                if recent_data:
                    # Calculate statistics
                    heights = [record.height for record in recent_data]
                    latest_height = recent_data[0].height
                    avg_height = sum(heights) / len(heights)
                    max_height = max(heights)
                    min_height = min(heights)
                    
                    # Get trend (comparing first 5 vs last 5 records)
                    if len(recent_data) >= 6:
                        first_half = heights[:len(heights)//2]
                        second_half = heights[len(heights)//2:]
                        trend = "rising" if sum(second_half)/len(second_half) > sum(first_half)/len(first_half) else "falling"
                    else:
                        trend = "stable"
                    
                    river_data[river_name] = {
                        'latest_height': latest_height,
                        'average_height': round(avg_height, 2),
                        'max_height': max_height,
                        'min_height': min_height,
                        'trend': trend,
                        'data_points': len(recent_data),
                        'latest_timestamp': recent_data[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    river_data[river_name] = {
                        'latest_height': 0,
                        'average_height': 0,
                        'max_height': 0,
                        'min_height': 0,
                        'trend': 'no_data',
                        'data_points': 0,
                        'latest_timestamp': 'No data available'
                    }
                    
            except Exception as e:
                print(f"Error getting data for {river_name}: {e}")
                river_data[river_name] = {
                    'latest_height': 0,
                    'average_height': 0,
                    'max_height': 0,
                    'min_height': 0,
                    'trend': 'error',
                    'data_points': 0,
                    'latest_timestamp': 'Error retrieving data'
                }
        
        return river_data
    
    def get_weather_data(self, hours_back=24):
        """Get weather data from all locations for the last N hours"""
        end_time = datetime.now(pytz.timezone('Asia/Colombo'))
        start_time = end_time - timedelta(hours=hours_back)
        
        weather_data = {}
        
        # Weather models and their names
        weather_models = [
            (PelmadullaWeather, 'Pelmadulla'),
            (RatnapuraWeather, 'Ratnapura'),
            (KalawanaWeather, 'Kalawana'),
            (KuruvitaWeather, 'Kuruvita'),
            (AyagamaWeather, 'Ayagama'),
            (KahawattaWeather, 'Kahawatta')
        ]
        
        for model_class, location_name in weather_models:
            try:
                # Get recent weather data
                recent_data = model_class.query.filter(
                    model_class.timestamp >= start_time,
                    model_class.timestamp <= end_time
                ).order_by(model_class.timestamp.desc()).limit(5).all()
                
                if recent_data:
                    latest = recent_data[0]
                    
                    # Calculate average precipitation
                    precip_values = [record.precip_mm for record in recent_data if record.precip_mm is not None]
                    avg_precip = sum(precip_values) / len(precip_values) if precip_values else 0
                    
                    weather_data[location_name] = {
                        'temperature_c': latest.temperature_c,
                        'humidity': latest.humidity,
                        'precip_mm': latest.precip_mm,
                        'avg_precip_24h': round(avg_precip, 2),
                        'pressure_mb': latest.pressure_mb,
                        'wind_kph': latest.wind_kph,
                        'wind_dir': latest.wind_dir,
                        'condition': latest.condition,
                        'cloud': latest.cloud,
                        'visibility_km': latest.visibility_km,
                        'timestamp': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    weather_data[location_name] = {
                        'temperature_c': 0,
                        'humidity': 0,
                        'precip_mm': 0,
                        'avg_precip_24h': 0,
                        'pressure_mb': 0,
                        'wind_kph': 0,
                        'wind_dir': 'N',
                        'condition': 'No data',
                        'cloud': 0,
                        'visibility_km': 0,
                        'timestamp': 'No data available'
                    }
                    
            except Exception as e:
                print(f"Error getting weather data for {location_name}: {e}")
                weather_data[location_name] = {
                    'temperature_c': 0,
                    'humidity': 0,
                    'precip_mm': 0,
                    'avg_precip_24h': 0,
                    'pressure_mb': 0,
                    'wind_kph': 0,
                    'wind_dir': 'N',
                    'condition': 'Error',
                    'cloud': 0,
                    'visibility_km': 0,
                    'timestamp': 'Error retrieving data'
                }
        
        return weather_data
    
    def create_analysis_prompt(self, river_data, weather_data):
        """Create a comprehensive prompt for Gemini AI analysis"""
        
        prompt = f"""
You are an expert hydrologist and flood risk assessment specialist analyzing data for Ratnapura, Sri Lanka. 

**ANALYSIS REQUEST:**
Predict the flood risk level for Ratnapura based on the following comprehensive data:

**RIVER HEIGHT DATA (Last 24 hours):**
"""
        
        # Add river data to prompt
        for river_name, data in river_data.items():
            prompt += f"""
- {river_name}:
  * Latest Height: {data['latest_height']}m
  * Average Height: {data['average_height']}m
  * Max Height: {data['max_height']}m
  * Min Height: {data['min_height']}m
  * Trend: {data['trend']}
  * Data Points: {data['data_points']}
  * Latest Update: {data['latest_timestamp']}
"""
        
        prompt += f"""

**WEATHER CONDITIONS (Last 24 hours):**
"""
        
        # Add weather data to prompt
        for location, data in weather_data.items():
            prompt += f"""
- {location}:
  * Temperature: {data['temperature_c']}°C
  * Humidity: {data['humidity']}%
  * Current Precipitation: {data['precip_mm']}mm
  * 24h Avg Precipitation: {data['avg_precip_24h']}mm
  * Pressure: {data['pressure_mb']}mb
  * Wind: {data['wind_kph']}km/h {data['wind_dir']}
  * Condition: {data['condition']}
  * Cloud Cover: {data['cloud']}%
  * Visibility: {data['visibility_km']}km
  * Last Update: {data['timestamp']}
"""
        
        prompt += f"""

**ANALYSIS CRITERIA:**
Consider these factors in your assessment:

1. **River Height Analysis:**
   - Current water levels vs historical averages
   - Rising/falling trends in all rivers
   - Kalu Ganga (main river) height specifically
   - Upstream river contributions

2. **Weather Impact:**
   - Current and recent precipitation patterns
   - Rainfall intensity and duration
   - Weather conditions across all locations
   - Atmospheric pressure changes

3. **Flood Risk Factors:**
   - River capacity and overflow potential
   - Upstream water accumulation
   - Weather system persistence
   - Historical flood patterns

**REQUIRED OUTPUT FORMAT:**
Provide your analysis in this exact JSON format:

{{
    "risk_level": "LOW|MODERATE|HIGH|CRITICAL",
    "confidence": 85,
    "primary_factors": [
        "Factor 1",
        "Factor 2",
        "Factor 3"
    ],
    "river_analysis": {{
        "kalu_ganga_status": "Description of Kalu Ganga condition",
        "upstream_impact": "Analysis of upstream river contributions",
        "trend_analysis": "Overall river height trend analysis"
    }},
    "weather_analysis": {{
        "precipitation_impact": "Analysis of rainfall impact",
        "weather_patterns": "Analysis of weather conditions",
        "atmospheric_pressure": "Analysis of pressure changes"
    }},
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        "Recommendation 3"
    ],
    "prediction_notes": "Additional insights and predictions",
    "next_assessment": "When to reassess (in hours)"
}}

**IMPORTANT:**
- Base your assessment on the actual data provided
- Consider the interconnected nature of the river system
- Account for weather patterns across all locations
- Provide specific, actionable recommendations
- Be conservative in risk assessment for safety
- Respond ONLY with the JSON format above, no additional text
"""
        
        return prompt
    
    def predict_flood_risk(self, hours_back=24):
        """Main prediction method"""
        try:
            print("🔍 Collecting river and weather data...")
            
            # Get data
            river_data = self.get_river_data(hours_back)
            weather_data = self.get_weather_data(hours_back)
            
            print("🤖 Analyzing data with Gemini AI...")
            
            # Create prompt
            prompt = self.create_analysis_prompt(river_data, weather_data)
            
            # Get prediction from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                # Extract JSON from response
                response_text = response.text.strip()
                
                # Find JSON in response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    prediction = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Add metadata
                prediction['analysis_timestamp'] = datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S')
                prediction['data_sources'] = {
                    'rivers_analyzed': len(river_data),
                    'weather_locations': len(weather_data),
                    'analysis_period_hours': hours_back
                }
                
                print("✅ Flood risk prediction completed")
                return prediction
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing Gemini response: {e}")
                print(f"Response: {response.text}")
                return self._create_fallback_prediction(river_data, weather_data)
                
        except Exception as e:
            print(f"❌ Error in flood risk prediction: {e}")
            return self._create_error_prediction(str(e))
    
    def _create_fallback_prediction(self, river_data, weather_data):
        """Create a basic prediction when Gemini fails"""
        # Simple heuristic-based prediction
        kalu_ganga = river_data.get('Kalu Ganga (Ratnapura)', {})
        ratnapura_weather = weather_data.get('Ratnapura', {})
        
        risk_level = "LOW"
        confidence = 50
        
        # Basic risk assessment
        if kalu_ganga.get('latest_height', 0) > 5.0:
            risk_level = "HIGH"
        elif kalu_ganga.get('latest_height', 0) > 3.0:
            risk_level = "MODERATE"
        
        if ratnapura_weather.get('precip_mm', 0) > 10:
            if risk_level == "LOW":
                risk_level = "MODERATE"
            elif risk_level == "MODERATE":
                risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "primary_factors": ["Basic heuristic analysis", "Limited data analysis"],
            "river_analysis": {
                "kalu_ganga_status": f"Height: {kalu_ganga.get('latest_height', 0)}m",
                "upstream_impact": "Analysis unavailable",
                "trend_analysis": kalu_ganga.get('trend', 'unknown')
            },
            "weather_analysis": {
                "precipitation_impact": f"Current: {ratnapura_weather.get('precip_mm', 0)}mm",
                "weather_patterns": ratnapura_weather.get('condition', 'Unknown'),
                "atmospheric_pressure": f"Pressure: {ratnapura_weather.get('pressure_mb', 0)}mb"
            },
            "recommendations": [
                "Monitor river levels closely",
                "Check weather updates regularly",
                "Prepare for potential flooding"
            ],
            "prediction_notes": "Fallback prediction due to AI analysis failure",
            "next_assessment": "2",
            "analysis_timestamp": datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S'),
            "data_sources": {
                "rivers_analyzed": len(river_data),
                "weather_locations": len(weather_data),
                "analysis_period_hours": 24
            }
        }
    
    def _create_error_prediction(self, error_message):
        """Create error prediction when system fails"""
        return {
            "risk_level": "UNKNOWN",
            "confidence": 0,
            "primary_factors": ["System error", "Data unavailable"],
            "river_analysis": {
                "kalu_ganga_status": "Data unavailable",
                "upstream_impact": "Analysis failed",
                "trend_analysis": "Unknown"
            },
            "weather_analysis": {
                "precipitation_impact": "Data unavailable",
                "weather_patterns": "Unknown",
                "atmospheric_pressure": "Unknown"
            },
            "recommendations": [
                "Check system status",
                "Verify data connections",
                "Manual monitoring recommended"
            ],
            "prediction_notes": f"System error: {error_message}",
            "next_assessment": "1",
            "analysis_timestamp": datetime.now(pytz.timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S'),
            "data_sources": {
                "rivers_analyzed": 0,
                "weather_locations": 0,
                "analysis_period_hours": 0
            }
        }

# Convenience functions
def predict_flood_risk(hours_back=24):
    """Predict flood risk for Ratnapura"""
    predictor = FloodRiskPredictor()
    return predictor.predict_flood_risk(hours_back)

def get_risk_level_info(risk_level):
    """Get information about a risk level"""
    predictor = FloodRiskPredictor()
    return predictor.risk_levels.get(risk_level, {
        'level': 0,
        'color': 'gray',
        'description': 'Unknown risk level'
    })

def format_prediction_for_display(prediction):
    """Format prediction for display in UI"""
    if not prediction:
        return "No prediction available"
    
    risk_info = get_risk_level_info(prediction.get('risk_level', 'UNKNOWN'))
    
    return {
        'risk_level': prediction.get('risk_level', 'UNKNOWN'),
        'risk_color': risk_info['color'],
        'risk_description': risk_info['description'],
        'confidence': prediction.get('confidence', 0),
        'primary_factors': prediction.get('primary_factors', []),
        'recommendations': prediction.get('recommendations', []),
        'analysis_timestamp': prediction.get('analysis_timestamp', 'Unknown'),
        'next_assessment': prediction.get('next_assessment', 'Unknown')
    }

def get_full_prediction_data(hours_back=24):
    """Get complete prediction data for use in other parts of the app"""
    predictor = FloodRiskPredictor()
    return predictor.predict_flood_risk(hours_back)

def get_concise_prediction_summary(hours_back=24):
    """Get concise prediction summary for quick display"""
    prediction = get_full_prediction_data(hours_back)
    if not prediction:
        return {
            'risk_level': 'UNKNOWN',
            'confidence': 0,
            'summary': 'Prediction unavailable'
        }
    
    risk_level = prediction.get('risk_level', 'UNKNOWN')
    confidence = prediction.get('confidence', 0)
    primary_factors = prediction.get('primary_factors', [])
    
    # Create 2-line summary
    line1 = f"Flood Risk: {risk_level} (Confidence: {confidence}%)"
    if primary_factors:
        if len(primary_factors) >= 2:
            line2 = f"{primary_factors[0]}. {primary_factors[1]}."
        else:
            line2 = f"{primary_factors[0]}."
    else:
        line2 = "No additional factors available."
    
    return {
        'risk_level': risk_level,
        'confidence': confidence,
        'summary': f"{line1}\n{line2}",
        'full_data': prediction  # Include full data for detailed views
    }
