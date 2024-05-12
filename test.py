import os
import requests
from gpt_helpers import OpenAIHelper

# Initialize the OpenAI helper globally
ai_key = os.getenv('openai_api_key')
if not ai_key:
    raise ValueError("API key for OpenAI is not set in environment variables")
intent = "Your goal is to objectively judge rap lyrics, song by song, without bias, and produce a general tone of the song and analysis of said lyrics."
bot = OpenAIHelper(ai_key, intent_message=intent)

def get_lyrics(artist, title):
    """Fetch lyrics for a given song."""
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    response = requests.get(url)
    if response.status_code == 200 and 'lyrics' in response.json():
        return response.json()['lyrics']
    else:
        return "Lyrics not found"

def assess_tone(lyrics):
    """Assess the tone of the lyrics and return structured data."""
    prompt = "Analyze the tone, provide a brief description, and cite key lines from these lyrics:"
    example_format = """{
        "tone_category": "Example Tone Category",
        "description": "Example Description of the song's theme or message",
        "cited_lines": "Example lines from the song that illustrate the identified tone and theme"
    }"""
    response = bot.gpt_json(prompt, lyrics, example_format, model="gpt-3.5-turbo-0125")
    return response

def assess_rap_lyrics(artist, song_name):
    """Function to assess the tone of rap lyrics for a given artist and song."""
    lyrics = get_lyrics(artist, song_name)
    if lyrics != "Lyrics not found":
        tone_assessment = assess_tone(lyrics)
        return tone_assessment
    else:
        return {"error": "Lyrics not found"}

# Example usage of the function
if __name__ == "__main__":
    artist = 'Kendrick Lamar'
    title = 'not like us'
    result = assess_rap_lyrics(artist, title)
    print(result)