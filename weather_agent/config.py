#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

agent_keys = {
    "GOOGLE_API_KEY":os.getenv("GOOGLE_API_KEY"),
    "OPEN_AI_KEY":os.getenv("OPEN_AI_KEY"),
    "ANTHROPIC_KEY":os.getenv("ANTHROPIC_KEY")
    }

