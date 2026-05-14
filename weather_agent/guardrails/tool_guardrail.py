#!/usr/bin/env python3

import aiohttp
from typing import Optional
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

AFRICAN_COUNTRY_CODES = {
    "DZ", "AO", "BJ", "BW", "BF", "BI", "CM", "CV", "CF", "TD",
    "KM", "CG", "CD", "DJ", "EG", "GQ", "ER", "ET", "GA", "GM",
    "GH", "GN", "GW", "CI", "KE", "LS", "LR", "LY", "MG", "MW",
    "ML", "MR", "MU", "YT", "MA", "MZ", "NA", "NE", "NG", "RE",
    "RW", "SH", "ST", "SN", "SC", "SL", "SO", "ZA", "SS", "SD",
    "SZ", "TZ", "TG", "TN", "UG", "EH", "ZM", "ZW",
}


async def africa_only_tool_guardrail(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    """
    Before-tool callback that blocks get_current_weather calls for cities
    outside Africa. Returns None to allow execution, or a dict error to block.
    """
    if tool.name != "get_current_weather":
        return None

    city = args.get("city", "")
    if not city:
        return None

    print(f"--- Tool Guardrail: checking if '{city}' is in Africa ---")

    try:
        async with aiohttp.ClientSession() as session:
            geo = await session.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1}
            )
            geo_data = await geo.json()

        if not geo_data.get("results"):
            return {"error": f"Could not verify location for '{city}'. Please try a different city name."}

        country_code = geo_data["results"][0].get("country_code", "").upper()
        country_name = geo_data["results"][0].get("country", "Unknown")

        if country_code not in AFRICAN_COUNTRY_CODES:
            print(f"--- Tool Guardrail: '{city}' is in {country_name} ({country_code}) — blocked ---")
            tool_context.state["guardrail_non_african_city_blocked"] = True
            return {
                "error": (
                    f"Sorry, this service only provides weather for African cities. "
                    f"'{city.capitalize()}' is located in {country_name}, which is outside Africa."
                )
            }

        print(f"--- Tool Guardrail: '{city}' is in {country_name} ({country_code}) — allowed ---")
        return None

    except Exception as e:
        print(f"--- Tool Guardrail: geocoding check failed: {e} ---")
        return None
