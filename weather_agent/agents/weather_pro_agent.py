#!/usr/bin/env python3

from google.adk.agents import Agent
from ..tools.tools import get_current_weather

MODEL_GEMINI_2_5_PRO = "gemini-2.5-pro"

gemini_pro_agent = Agent(
    name="gemini_pro_weather_agent",
    model=MODEL_GEMINI_2_5_PRO,
    description="Provides a second opinion on weather queries using Gemini 2.5 Pro.",
    tools=[get_current_weather],
    instruction="""
    You are a detailed weather assistant powered by Gemini Pro.
    Use the get_current_weather tool whenever the user asks
    about weather conditions for a city.
    Provide thorough, thoughtful responses including clothing suggestions
    and activity recommendations based on the weather data.
    If the tool fails, explain the issue politely.
    """
    )
