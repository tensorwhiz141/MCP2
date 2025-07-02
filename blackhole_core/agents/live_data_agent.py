#!/usr/bin/env python3
"""
LiveDataAgent - Real-time weather info extractor
Fetches weather data from wttr.in API for a given location.
"""

import requests  # HTTP requests to external API
import re  # For extracting locations via regex
from datetime import datetime  # Timestamping responses
from bson import ObjectId  # MongoDB ObjectId support
from blackhole_core.data_source.mongodb import get_mongo_client  # MongoDB client

class LiveDataAgent:
    def __init__(self, memory=None, api_url=None):
        """Initialize LiveDataAgent with memory, API endpoint, and MongoDB."""
        self.memory = memory
        self.base_api_url = "https://wttr.in"  # Base weather API URL
        self.client = get_mongo_client()
        self.db = self.client["blackhole_db"]  # Reference to database

        # Location patterns to extract city names from queries
        self.location_patterns = [
            r'weather\s+(?:in|for|at)\s+([a-zA-Z\s]+)',
            r'temperature\s+(?:in|for|at)\s+([a-zA-Z\s]+)',
            r'(?:in|for|at)\s+([a-zA-Z\s]+)\s+weather',
            r'(?:in|for|at)\s+([a-zA-Z\s]+)\s+temperature',
            r'weather\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+weather'
        ]

    def plan(self, query):
        """
        🔍 Input: query containing city name
        ⚙️ Processing: extract location and call wttr.in API
        🧾 Output: full weather data and metadata
        """
        try:
            location = self._extract_location(query)  # 🔍 Extract location
            api_url = f"{self.base_api_url}/{location}?format=j1"  # Build full URL
            response = requests.get(api_url, timeout=10)  # Call API
            data = response.json()  # Parse response JSON

            # 🧾 Construct result object
            result = {
                "agent": "LiveDataAgent",
                "input": query,
                "output": data,
                "location_requested": location,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"api_url": api_url}
            }
        except Exception as e:
            # If anything fails, return the error
            result = {
                "agent": "LiveDataAgent",
                "input": query,
                "output": f"Error fetching data: {e}",
                "location_requested": location if 'location' in locals() else "Unknown",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"api_url": api_url if 'api_url' in locals() else "N/A"}
            }

        return result

    def _extract_location(self, query):
        """
        Extract location from query using regex or fallback mappings.

        Returns:
            city name (str)
        """
        # Normalize query
        if isinstance(query, dict):
            query_text = query.get('query', '') or query.get('document_text', '') or str(query)
        else:
            query_text = str(query)

        query_lower = query_text.lower().strip()

        # Apply regex patterns
        for pattern in self.location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                location = self._clean_location(location)
                if location:
                    return location

        # Known cities and their corrections
        city_mappings = {
            'banglore': 'bangalore', 'bengaluru': 'bangalore', 'bombay': 'mumbai',
            'calcutta': 'kolkata', 'madras': 'chennai', 'new delhi': 'delhi',
            'ny': 'new york', 'nyc': 'new york', 'la': 'los angeles',
            'sf': 'san francisco', 'london uk': 'london', 'paris france': 'paris',
            'tokyo japan': 'tokyo',
            'mumbai': 'mumbai', 'delhi': 'delhi', 'bangalore': 'bangalore',
            'chennai': 'chennai', 'kolkata': 'kolkata', 'hyderabad': 'hyderabad',
            'pune': 'pune', 'ahmedabad': 'ahmedabad', 'london': 'london',
            'paris': 'paris', 'tokyo': 'tokyo', 'new york': 'new york',
            'los angeles': 'los angeles', 'chicago': 'chicago', 'sydney': 'sydney',
            'melbourne': 'melbourne', 'toronto': 'toronto', 'vancouver': 'vancouver',
            'berlin': 'berlin', 'madrid': 'madrid'
        }

        for variant, correct in city_mappings.items():
            if variant in query_lower:
                return correct.title()

        for variant, correct in city_mappings.items():
            if self._is_similar_city(query_lower, variant):
                return correct.title()

        return "London"  # Default fallback

    def _clean_location(self, location):
        """
        Remove stopwords and standardize city name capitalization.
        """
        if not location:
            return None

        stop_words = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'weather', 'temperature', 'climate']
        words = location.split()
        cleaned = [w for w in words if w.lower() not in stop_words]
        if not cleaned:
            return None

        cleaned_location = ' '.join(cleaned).title()

        location_mappings = {
            'Ny': 'New York', 'La': 'Los Angeles', 'Sf': 'San Francisco',
            'Uk': 'London', 'Us': 'New York'
        }

        return location_mappings.get(cleaned_location, cleaned_location)

    def _is_similar_city(self, query_text: str, city_name: str) -> bool:
        """
        Basic fuzzy matcher for misspelled city names.
        """
        if len(city_name) < 4:
            return False
        max_differences = 1 if len(city_name) <= 6 else 2

        # Basic fuzzy check - here just direct substring match
        if city_name not in query_text:
            return False

        return True