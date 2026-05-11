#!/usr/bin/env python3

import asyncio
import aiohttp

async def get_current_weather(city:str):
    """this async function get current city"""
    city = city.lower()

    # current latitude and longitude
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    async with aiohttp.ClientSession() as session:
        geo = await session.get(geo_url, params={"name":city, "count":1})
        geo_data = await geo.json()
        if not geo_data.get("results"):
            return {
                "error":f"{city} not found"
            }
        latitude = geo_data["results"][0]["latitude"]
        longitude = geo_data["results"][0]["longitude"]

        # current current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather = await session.get(weather_url, params={
            "latitude":latitude,
            "longitude":longitude,
            "current_weather":"true"
        })
        data = await weather.json()
    return {
        "current_city": f"{city[0].upper() + city[1:]}",
        "temperature_c": data["current_weather"]["temperature"],
        "windspeed_kmh": data["current_weather"]["windspeed"],
        "condition_code": data["current_weather"]["weathercode"]
    }

async def get_current_time(city: str):
    """Get the current time for a given city."""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    async with aiohttp.ClientSession() as session:
        geo = await session.get(geo_url, params={"name": city, "count": 1})
        geo_data = await geo.json()
        if not geo_data.get("results"):
            return {"error": f"City '{city}' not found"}

        timezone = geo_data["results"][0]["timezone"]

        time_url = "https://timeapi.io/api/time/current/zone"
        response = await session.get(time_url, params={"timeZone": timezone})
        data = await response.json()

    return {
        "city": city.capitalize(),
        "timezone": timezone,
        "datetime": data["dateTime"],
        "day_of_week": data["dayOfWeek"]
    }

if __name__ == "__main__":
    print(asyncio.run(get_current_weather(city="Kigali")))
    print(asyncio.run(get_current_time(city="Kigali")))
