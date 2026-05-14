#!/usr/bin/env python3

import uuid
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .tools import get_current_weather

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"
MODEL_GEMINI_2_5_PRO = "gemini-2.5-pro"

try:
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

    root_agent = Agent(
        name="weather_coordinator",
        model=MODEL_GEMINI_2_5_FLASH,
        description="Coordinator that delegates weather queries to Gemini Flash or Gemini Pro agents.",
        sub_agents=[gemini_flash_agent, gemini_pro_agent],
        instruction="""
        You are a coordinator for weather queries.
        - Delegate to gemini_flash_weather_agent by default.
        - Delegate to gemini_pro_weather_agent if the user asks for a second opinion or more detail.
        """
        )

    APP_NAME = "weather_tutorial_app"
    USER_ID = str(uuid.uuid4())
    SESSION_ID = str(uuid.uuid4())

    async def setup_runner():
        """
        This async function setup a new runner
        """
        session_service_gpt = InMemorySessionService()
        await session_service_gpt.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        return Runner(agent=root_agent,
                    app_name=APP_NAME,
                    session_service=session_service_gpt
                    )

    async def call_agent_back(query:str, runner:Runner, user_id:str, session_id:str):
        """
        This function sends a query to an agent and print the final response
        Args:
            query:str
            runner
            user_id:str
            session_id:str
        return
        """

        user_message = types.Content(role="user", parts=[types.Part(text=query)])
        async for event in runner.run_async(user_id=user_id,
                                            session_id=session_id,
                                            new_message=user_message):
            print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_text = event.content.parts[0].text

                elif event.actions and event.actions.escalate:
                    final_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                print(f"<<< Agent Response: {final_text}")
                break

except Exception as error:
    print(f"An error occured:\n\t{error}")

async def run_conversation():
    """
    run the conversation
    """
    query:str|None = input().strip()
    if not query:
        return

    runner = await setup_runner()

    await call_agent_back(
        query=query,
        runner =runner,
        user_id=USER_ID,
        session_id=SESSION_ID
        )

if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as error:
        print(f"An error occured:\n\t{error}")
