#!/usr/bin/env python3

from google.adk.agents.llm_agent import Agent

def get_time_weather(city:str):
    """This simple tool returns the time and weather"""
    return {
        "city":"city_name",
        "time":"current_time",
        "weather":"current_weather in celcius"
    }

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[get_time_weather]
)

