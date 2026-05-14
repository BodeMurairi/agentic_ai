#!/usr/bin/env python3

from google.adk.agents import Agent
from ..tools.tools import get_current_weather

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"

gemini_flash_agent = Agent(
        name="gemini_flash_weather_agent",
        model=MODEL_GEMINI_2_5_FLASH,
        description="Handles weather queries using Gemini 2.5 Flash.",
        tools=[get_current_weather],
        instruction="""
        You are a helpful weather assistant powered by Gemini Flash.
        Use the get_current_weather tool whenever the user asks
        about weather conditions for a city.
        If the user does not specify a city, ask a concise follow-up question.
        If the tool fails, explain the issue politely.
        Keep responses concise and readable.
        """
        )
