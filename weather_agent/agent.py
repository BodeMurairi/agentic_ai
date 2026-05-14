#!/usr/bin/env python3

import uuid
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .tools import get_current_weather

MODEL_GEMINI_2_5_FLASH = "gemini-flash-latest"
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "claude-sonnet-4-6"

root_agent = Agent(
    name="weather_agent_v1",
    model=MODEL_GEMINI_2_5_FLASH,
    description="Provides weather information for specific cities.",
    tools=[get_current_weather],
    instruction="""
    You are a helpful weather assistant.
    Use the get_current_weather tool whenever the user asks
    about weather conditions for a city.
    If the user does not specify a city, ask a concise follow-up question.
    If the tool fails, explain the issue politely.
    Keep responses concise and readable.
    """
    )

APP_NAME = "weather_tutorial_app"
USER_ID = str(uuid.uuid4()).split()[0]
SESSION_ID = str(uuid.uuid4()).split()[1]

async def setup_runner():
    """
    This async function setup a new runner
    """
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    return Runner(agent=root_agent,
                  app_name=APP_NAME,
                  session_service=session_service
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
