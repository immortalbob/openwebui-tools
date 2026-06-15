"""
Open-Meteo Forecast Tool for Open WebUI
Fetches weather forecast for Kingman, AZ from Open-Meteo (no API key required).

Install in Open WebUI: Workspace → Tools → Create Tool
Paste this file contents into the tool editor and save.

Requires: requests (available in Open WebUI's environment)
"""

import requests
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        LATITUDE: float = Field(
            default=35.1894,
            description="Latitude of the forecast location"
        )
        LONGITUDE: float = Field(
            default=-114.0530,
            description="Longitude of the forecast location"
        )
        LOCATION_NAME: str = Field(
            default="Kingman, Arizona",
            description="Human-readable location name for responses"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _degrees_to_cardinal(self, degrees: float) -> str:
        directions = [
            "north", "north-northeast", "northeast", "east-northeast",
            "east", "east-southeast", "southeast", "south-southeast",
            "south", "south-southwest", "southwest", "west-southwest",
            "west", "west-northwest", "northwest", "north-northwest"
        ]
        index = int(((degrees + 11.25) % 360) / 22.5)
        return directions[index]

    def _round_speech(self, value: float) -> int:
        """Round to nearest 5 for natural speech."""
        return round(value / 5) * 5

    def get_forecast(self, query: str = "") -> str:
        """
        Get the weather forecast for the configured location.
        Use this when the user asks about future weather conditions such as
        'will it rain', 'what's the forecast', 'tomorrow's weather',
        'this weekend', 'later today', or any question about upcoming conditions.

        :param query: The user's forecast question for context (e.g. 'will it rain tomorrow')
        :return: Conversational plain-text weather forecast
        """
        try:
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": self.valves.LATITUDE,
                    "longitude": self.valves.LONGITUDE,
                    "hourly": "temperature_2m,precipitation_probability,weathercode,windspeed_10m,winddirection_10m",
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant,sunrise,sunset",
                    "temperature_unit": "fahrenheit",
                    "windspeed_unit": "mph",
                    "precipitation_unit": "inch",
                    "timezone": "America/Phoenix",
                    "forecast_days": 3,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            return f"Unable to retrieve forecast data: {e}"

        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        wmo_descriptions = {
            0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
            45: "foggy", 48: "foggy",
            51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
            61: "light rain", 63: "rain", 65: "heavy rain",
            71: "light snow", 73: "snow", 75: "heavy snow",
            77: "snow grains",
            80: "light showers", 81: "showers", 82: "heavy showers",
            85: "snow showers", 86: "heavy snow showers",
            95: "thunderstorms", 96: "thunderstorms with hail", 99: "thunderstorms with heavy hail",
        }

        def describe(code):
            return wmo_descriptions.get(int(code), "mixed conditions")

        def sunrise_sunset(iso_str):
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%-I:%M %p").lower()

        lines = []

        # Today
        today_high = round(daily["temperature_2m_max"][0])
        today_low = round(daily["temperature_2m_min"][0])
        today_code = daily["weathercode"][0]
        today_precip = daily["precipitation_probability_max"][0]
        today_wind = round(daily["windspeed_10m_max"][0])
        today_dir = self._degrees_to_cardinal(daily["winddirection_10m_dominant"][0])
        today_rise = sunrise_sunset(daily["sunrise"][0])
        today_set = sunrise_sunset(daily["sunset"][0])

        today_str = f"Today will be {describe(today_code)} with a high of about {today_high} and a low of {today_low}."
        if today_precip >= 20:
            today_str += f" There's a {today_precip}% chance of precipitation."
        if today_wind >= 15:
            today_str += f" Winds out of the {today_dir} around {today_wind} miles per hour."
        today_str += f" Sunrise at {today_rise}, sunset at {today_set}."
        lines.append(today_str)

        # Tomorrow
        tom_high = round(daily["temperature_2m_max"][1])
        tom_low = round(daily["temperature_2m_min"][1])
        tom_code = daily["weathercode"][1]
        tom_precip = daily["precipitation_probability_max"][1]
        tom_wind = round(daily["windspeed_10m_max"][1])
        tom_dir = self._degrees_to_cardinal(daily["winddirection_10m_dominant"][1])

        tom_str = f"Tomorrow looks {describe(tom_code)}, high of {tom_high}, low of {tom_low}."
        if tom_precip >= 20:
            tom_str += f" {tom_precip}% chance of rain."
        if tom_wind >= 15:
            tom_str += f" Winds from the {tom_dir} around {tom_wind} miles per hour."
        lines.append(tom_str)

        # Day after
        day3_date = datetime.fromisoformat(daily["time"][2]).strftime("%A")
        day3_high = round(daily["temperature_2m_max"][2])
        day3_low = round(daily["temperature_2m_min"][2])
        day3_code = daily["weathercode"][2]
        day3_precip = daily["precipitation_probability_max"][2]

        day3_str = f"{day3_date} is looking {describe(day3_code)}, high of {day3_high}, low of {day3_low}."
        if day3_precip >= 20:
            day3_str += f" {day3_precip}% chance of precipitation."
        lines.append(day3_str)

        return " ".join(lines)
