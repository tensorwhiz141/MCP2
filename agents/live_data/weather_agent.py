# #!/usr/bin/env python3
# """
# Real-Time Weather Agent - Live Weather Data Only
# Uses OpenWeatherMap API exclusively for real-time weather data
# """

# import os
# import sys
# import requests
# import json
# import re
# from datetime import datetime, timedelta
# from typing import Dict, List, Any, Optional
# import logging
# from dotenv import load_dotenv
# load_dotenv()


# # Add project root to path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# from agents.base_agent import BaseMCPAgent, AgentCapability, MCPMessage

# class RealTimeWeatherAgent(BaseMCPAgent):
#     """Real-time weather agent that fetches live data from OpenWeatherMap API only."""

#     def __init__(self):
#         capabilities = [
#             AgentCapability(
#                 name="realtime_weather",
#                 description="Fetch real-time weather data from OpenWeatherMap API",
#                 input_types=["text", "dict"],
#                 output_types=["dict"],
#                 methods=["get_weather", "get_forecast", "process", "info"]
#             )
#         ]

#         super().__init__("realtime_weather_agent", "Real-Time Weather Agent", capabilities)

#         self.api_key = os.getenv('OPENWEATHER_API_KEY', '').strip()
#         # self.base_url = os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5').strip()
#         # self.units = os.getenv('WEATHER_UNITS', 'metric').strip()
#         # self.language = os.getenv('WEATHER_LANGUAGE', 'en').strip()

#         self.city_corrections = {
#             'mumbai': 'Mumbai,IN', 'delhi': 'New Delhi,IN', 'bangalore': 'Bangalore,IN',
#             'chennai': 'Chennai,IN', 'kolkata': 'Kolkata,IN', 'pune': 'Pune,IN'
#             # Add more if needed
#         }

#         if not self.api_key or len(self.api_key) < 10:
#             self.logger.warning("OpenWeatherMap API key not configured properly.")
#         else:
#             self.logger.info(f"Weather agent initialized with key: {self.api_key[:6]}...")

#     async def handle_process(self, message: MCPMessage) -> Dict[str, Any]:
#         query = message.params.get("query", "")
#         city = self.extract_city_name(query)

#         if not self.api_key:
#             return {
#                 "status": "error",
#                 "message": "API key is not set. Please check your .env file.",
#                 "agent": self.agent_id
#             }

#         if not city:
#             return {
#                 "status": "error",
#                 "message": "Could not determine city from query.",
#                 "agent": self.agent_id
#             }

#         return await self.get_weather(city)

#     def extract_city_name(self, query: str) -> Optional[str]:
#         query = query.lower().strip()
#         for pattern in [
#             r'weather\s+(?:in|of|for)\s+([a-zA-Z\s]+)',
#             r'temperature\s+(?:in|of|for)\s+([a-zA-Z\s]+)'
#         ]:
#             match = re.search(pattern, query)
#             if match:
#                 city = match.group(1).strip()
#                 return self.city_corrections.get(city, city.title())
#         return None

#     async def get_weather(self, city: str) -> Dict[str, Any]:
#         try:
#             url = f"{self.base_url}/weather"
#             params = {
#                 "q": city,
#                 "appid": self.api_key,
#                 "units": self.units,
#                 "lang": self.language
#             }
#             res = requests.get(url, params=params)
#             if res.status_code != 200:
#                 return {
#                     "status": "error",
#                     "message": f"API error {res.status_code}: {res.json().get('message')}",
#                     "agent": self.agent_id
#                 }

#             data = res.json()
#             return {
#                 "status": "success",
#                 "city": data["name"],
#                 "country": data["sys"]["country"],
#                 "temperature": data["main"]["temp"],
#                 "description": data["weather"][0]["description"],
#                 "humidity": data["main"]["humidity"],
#                 "wind_speed": data["wind"]["speed"],
#                 "timestamp": datetime.now().isoformat(),
#                 "agent": self.agent_id
#             }

#         except Exception as e:
#             return {
#                 "status": "error",
#                 "message": str(e),
#                 "agent": self.agent_id
#             }

#     async def handle_info(self, message: MCPMessage) -> Dict[str, Any]:
#         return {
#             "status": "success",
#             "agent": self.agent_id,
#             "info": "Returns live weather data using OpenWeatherMap."
#         }

# def get_agent_info():
#     return {
#         "name": "Real-Time Weather Agent",
#         "description": "Fetches live weather data from OpenWeatherMap",
#         "version": "1.0.0",
#         "author": "MCP System",
#         "capabilities": ["realtime_weather"],
#         "category": "data"
#     }

# def create_agent():
#     return RealTimeWeatherAgent()
import sys
import os
import requests
# from dotenv import load_dotenv
from agents.base_agent import BaseMCPAgent
from dotenv import load_dotenv

# load_dotenv()
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
print("📁 Looking for .env at:", dotenv_path)

load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENWEATHER_API_KEY")
print("🔑 API Key loaded:", api_key)


class WeatherAgent(BaseMCPAgent):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

        if not self.api_key or self.api_key.strip() == "your-api-key":
            raise ValueError("❌ OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY in your .env file.")

        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_agent_info(self):
        return {
            "id": "weather_agent",
            "description": "Fetches real-time weather data using OpenWeatherMap API"
        }

    async def process_message(self, message):
        query = message.params.get("query", "").lower()
        location = self.extract_location(query)

        if not location:
            return {
                "status": "error",
                "message": "⚠️ Could not extract location from input."
            }

        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if response.status_code == 200:
                weather = data["weather"][0]["description"]
                temperature = data["main"]["temp"]

                return {
                    "status": "success",
                    "location": location,
                    "weather": weather,
                    "temperature": temperature,
                    "units": "Celsius"
                }

            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to fetch weather data")
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Weather API request failed: {str(e)}"
            }

    def extract_location(self, query):
        # Simplified example — in production, use NLP
        for word in query.split():
            if word[0].isupper():  # assume city names are capitalized
                return word
        return None
