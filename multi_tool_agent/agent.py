#!/usr/bin/env python3

from .tools import get_current_weather, get_current_time
from google.adk.agents import Agent

root_agent = Agent(
    name="weather_specialist_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_current_time, get_current_weather]
    )
