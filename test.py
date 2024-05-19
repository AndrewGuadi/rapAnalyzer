import os
import requests
from gpt_helpers import OpenAIHelper

# Initialize the OpenAI helper globally
ai_key = os.getenv('openai_api_key')
if not ai_key:
    raise ValueError("API key for OpenAI is not set in environment variables")
intent = "Your goal is to objectively judge rap lyrics, song by song, without bias, and produce a general tone of the song and analysis of said lyrics."
bot = OpenAIHelper(ai_key, intent_message=intent)

prompt = "Hello"
response = bot.gpt_4(prompt)
print(response)