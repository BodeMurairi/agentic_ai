#!/usr/bin/env python3

import aiohttp
from typing import Optional
from google.adk.tools import ToolContext


def greeting(name: Optional[str], tool_context: ToolContext) -> str:
    """
    Greet the user by name and save their name to session state.
    Args:
        name: Optional user name
        tool_context: ADK tool context for reading/writing session state
    """
    if name:
        tool_context.state["user_name"] = name

    stored_name = tool_context.state.get("user_name")
    if not stored_name:
        return "Hello there!"
    return f"Hello {stored_name}!"


def say_goodbye(tool_context: ToolContext) -> str:
    """
    Say goodbye, personalised with the user's name if known from session state.
    Args:
        tool_context: ADK tool context for reading session state
    """
    name = tool_context.state.get("user_name")
    if name:
        return f"Goodbye {name}! Have a wonderful day!"
    return "Great to interact with you. Have a wonderful day!"


def set_temperature_unit(unit: str, tool_context: ToolContext) -> str:
    """
    Update the user's preferred temperature unit in session state.
    Args:
        unit: Temperature unit — either 'Celsius' or 'Fahrenheit'
        tool_context: ADK tool context for writing session state
    """
    unit = unit.strip().capitalize()
    if unit not in ("Celsius", "Fahrenheit"):
        return "Invalid unit. Please choose 'Celsius' or 'Fahrenheit'."
    tool_context.state["user_preference_temperature_unit"] = unit
    return f"Temperature unit updated to {unit}."


async def get_current_weather(city: str, tool_context: ToolContext):
    """
    Get the current weather for a city and update session state.
    Returns temperature in the user's preferred unit (Celsius or Fahrenheit).
    Args:
        city: Name of the city
        tool_context: ADK tool context for reading/writing session state
    """
    city = city.lower()

    tool_context.state["last_city"] = city

    history: list = tool_context.state.get("query_history", [])
    if city not in history:
        history.append(city)
    tool_context.state["query_history"] = history

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    async with aiohttp.ClientSession() as session:
        geo = await session.get(geo_url, params={"name": city, "count": 1})
        geo_data = await geo.json()
        if not geo_data.get("results"):
            return {"error": f"{city} not found"}

        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather = await session.get(weather_url, params={
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        })
        data = await weather.json()

    temp_c = data["current_weather"]["temperature"]
    unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")

    if unit == "Fahrenheit":
        temperature = round((temp_c * 9 / 5) + 32, 1)
    else:
        temperature = temp_c

    return {
        "current_city": city[0].upper() + city[1:],
        f"temperature_{unit[0].lower()}": temperature,
        "unit": unit,
        "windspeed_kmh": data["current_weather"]["windspeed"],
        "condition_code": data["current_weather"]["weathercode"]
    }
