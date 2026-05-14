#!/usr/bin/env python3

import uuid
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from .tools.tools import get_current_weather, set_temperature_unit
from .agents.weather_gemini_agent import gemini_flash_agent
from .agents.weather_pro_agent import gemini_pro_agent
from .agents.greeting_agent import greeting_agent, farewell_agent

from .guardrails.request_guardrail import block_keyword_guardrail
from .guardrails.tool_guardrail import africa_only_tool_guardrail

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"

initial_state = {
    "user_preference_temperature_unit": "Celsius",
    "user_name": None,
    "last_city": None,
    "query_history": [],
    "guardrail_block_keyword_triggered": False,
    "guardrail_non_african_city_blocked": False,
}

try:

    root_agent = Agent(
        name="weather_coordinator",
        model=MODEL_GEMINI_2_5_FLASH,
        sub_agents=[gemini_flash_agent, gemini_pro_agent, greeting_agent, farewell_agent],
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "You are state-aware: session state tracks 'user_name', 'last_city', 'query_history', and 'user_preference_temperature_unit'. "
                    "Use this context to give personalised responses — e.g. if 'last_city' is set and the user asks a follow-up without naming a city, reuse it. "
                    "If the user asks for temperature in Fahrenheit or Celsius, call 'set_temperature_unit' first to update their preference, then fetch the weather. "
                    "Use the 'get_current_weather' tool for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "3. 'gemini_pro_weather_agent': Provides a detailed second opinion. Delegate when the user asks for more detail or a second opinion. "
                    "4. 'gemini_flash_weather_agent': Handles standard weather queries quickly. Delegate when you prefer to offload. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_current_weather, set_temperature_unit],
        before_model_callback=block_keyword_guardrail,
        before_tool_callback=africa_only_tool_guardrail
        )

    APP_NAME = "weather_tutorial_app"
    USER_ID = str(uuid.uuid4())
    SESSION_ID = str(uuid.uuid4())

    async def setup_runner():
        """
        This async function setup a new runner
        """
        session_service_gpt = InMemorySessionService()
        await session_service_gpt.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=initial_state)
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
