"""
River Height Prediction Service using Gemini AI
Predicts river height trends (up, down, or same) based on current weather attributes
"""

import google.generativeai as genai
import json
from datetime import datetime
import pytz
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configure Gemini API
def configure_gemini():
    """Configure Gemini API with key from config"""
    try:
        if FLASK_AVAILABLE:
            api_key = current_app.config.get('GEMINI_API_KEY')
        else:
            # Fallback for testing outside Flask context
            api_key = "AIzaSyBQJQJQJQJQJQJQJQJQJQJQJQJQJQJQJQ"  # Replace with your actual API key
        
        if api_key:
            genai.configure(api_key=api_key)
            return True
        else:
            print("Warning: GEMINI_API_KEY not found in config")
            return False
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return False

class RiverPredictionService:
    """River height prediction using Gemini AI"""
    
    def __init__(self):
        # Configure Gemini API
        if configure_gemini():
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def predict_river_height_trend(self, weather_data, river_data):
        """
        Predict river height trend based on weather and current river data
        
        Args:
            weather_data (dict): Current weather data from WeatherAPI
            river_data (dict): Current river height data
            
        Returns:
            dict: Prediction result with trend and description
        """
        try:
            # Check if model is available
            if not self.model:
                return self._create_fallback_prediction(weather_data, river_data)
            
            # Create analysis prompt
            prompt = self._create_prediction_prompt(weather_data, river_data)
            
            # Get prediction from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                response_text = response.text.strip()
                
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    prediction = json.loads(json_str)
                    
                    # Add metadata
                    prediction['prediction_timestamp'] = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                    
                    return prediction
                else:
                    raise ValueError("No JSON found in response")
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini response: {e}")
                return self._create_fallback_prediction(weather_data, river_data)
                
        except Exception as e:
            print(f"Error in river height prediction: {e}")
            return self._create_error_prediction(str(e))
    
    def _create_prediction_prompt(self, weather_data, river_data):
        """Create prompt for Gemini AI analysis"""
        
        prompt = f"""
You are an expert hydrologist analyzing river height trends for Philippine rivers.

**CURRENT WEATHER CONDITIONS:**
- Location: {weather_data.get('location', 'Unknown')}
- Temperature: {weather_data.get('temperature_c', 0)}°C
- Condition: {weather_data.get('condition', 'Unknown')}
- Humidity: {weather_data.get('humidity', 0)}%
- Precipitation: {weather_data.get('precip_mm', 0)}mm
- Pressure: {weather_data.get('pressure_mb', 0)}mb
- Wind Speed: {weather_data.get('wind_kph', 0)}km/h
- Wind Direction: {weather_data.get('wind_dir', 'Unknown')}
- UV Index: {weather_data.get('uv', 0)}
- Visibility: {weather_data.get('visibility_km', 0)}km

**CURRENT RIVER DATA:**
- River Name: {river_data.get('river_name', 'Unknown')}
- Dam Name: {river_data.get('dam_name', 'Unknown')}
- Current Height: {river_data.get('current_height', 0)}m
- Observation Time: {river_data.get('observation_time', 'Unknown')}
- Observation Date: {river_data.get('observation_date', 'Unknown')}

**ANALYSIS CRITERIA:**
Consider these factors for river height prediction:

1. **Precipitation Impact:**
   - Current rainfall intensity and duration
   - Recent precipitation patterns
   - Seasonal rainfall expectations

2. **Weather Conditions:**
   - Temperature effects on evaporation
   - Humidity levels affecting water retention
   - Atmospheric pressure changes
   - Wind patterns affecting water flow

3. **River Characteristics:**
   - Current water level vs normal levels
   - Dam operations and reservoir levels
   - Upstream water contributions
   - Seasonal flow patterns

4. **Environmental Factors:**
   - Soil saturation levels
   - Groundwater contributions
   - Evapotranspiration rates

**PREDICTION REQUIREMENTS:**
Based on the current weather and river data, predict the river height trend for the next 6-12 hours.

**REQUIRED OUTPUT FORMAT:**
Provide your analysis in this exact JSON format:

{{
    "trend": "UP|DOWN|SAME",
    "confidence": 85,
    "magnitude": "LOW|MODERATE|HIGH",
    "timeframe": "6-12 hours",
    "reasoning": [
        "Primary factor affecting river height",
        "Secondary factor contributing to trend",
        "Additional environmental consideration"
    ],
    "description": "Clear, concise description of predicted river height trend",
    "risk_assessment": "LOW|MODERATE|HIGH",
    "recommendations": [
        "Action item 1",
        "Action item 2",
        "Action item 3"
    ]
}}

**IMPORTANT:**
- Base your assessment on the actual data provided
- Consider Philippine climate and river characteristics
- Be conservative in predictions for safety
- Focus on short-term trends (6-12 hours)
- Respond ONLY with the JSON format above, no additional text
"""
        
        return prompt
    
    def _create_fallback_prediction(self, weather_data, river_data):
        """Create basic prediction when Gemini fails"""
        
        # Simple heuristic-based prediction
        precip = weather_data.get('precip_mm', 0)
        humidity = weather_data.get('humidity', 0)
        current_height = river_data.get('current_height', 0)
        
        trend = "SAME"
        confidence = 50
        magnitude = "LOW"
        
        # Basic trend analysis
        if precip > 10:  # Heavy rain
            trend = "UP"
            magnitude = "HIGH"
            confidence = 80
        elif precip > 5:  # Moderate rain
            trend = "UP"
            magnitude = "MODERATE"
            confidence = 70
        elif precip > 0:  # Light rain
            trend = "UP"
            magnitude = "LOW"
            confidence = 60
        elif humidity < 30:  # Very dry conditions
            trend = "DOWN"
            magnitude = "LOW"
            confidence = 60
        
        return {
            "trend": trend,
            "confidence": confidence,
            "magnitude": magnitude,
            "timeframe": "6-12 hours",
            "reasoning": [
                f"Current precipitation: {precip}mm",
                f"Humidity level: {humidity}%",
                "Basic heuristic analysis"
            ],
            "description": f"River height expected to go {trend.lower()} based on current weather conditions",
            "risk_assessment": "LOW",
            "recommendations": [
                "Monitor weather conditions",
                "Check river levels regularly",
                "Stay informed about local conditions"
            ],
            "prediction_timestamp": datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _create_error_prediction(self, error_message):
        """Create prediction when error occurs"""
        return {
            "trend": "UNKNOWN",
            "confidence": 0,
            "magnitude": "UNKNOWN",
            "timeframe": "6-12 hours",
            "reasoning": [f"Prediction error: {error_message}"],
            "description": "Unable to predict river height trend due to technical error",
            "risk_assessment": "UNKNOWN",
            "recommendations": [
                "Check system status",
                "Monitor river levels manually",
                "Contact technical support if needed"
            ],
            "prediction_timestamp": datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        }

def predict_river_height_trend(weather_data, river_data):
    """
    Main function to predict river height trend
    
    Args:
        weather_data (dict): Current weather data
        river_data (dict): Current river height data
        
    Returns:
        dict: Prediction result
    """
    service = RiverPredictionService()
    return service.predict_river_height_trend(weather_data, river_data)
