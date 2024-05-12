from openai import OpenAI
from uuid import uuid4
import time
import base64
import requests
from pathlib import Path
from typing import Literal



class OpenAIHelper:
    def __init__(self, api_key, intent_message):
        self.api_key = api_key
        self.intent_message = intent_message
        self.messages=[ 
            {"role": "system", "content": f"{self.intent_message}"}
                       ]

        self.connect_to_openai()


    def connect_to_openai(self):
        self.client = OpenAI(api_key=self.api_key)


    def reset_messages(self):
        self.messages=[{"role": "system", "content": f"{self.intent_message}"}
                       ] 
        
    def gpt_3(self, prompt, max_retries=5):
        # Setup for entering into messages
        query_wrapper = {"role": "user", "content": f"{prompt}"}
        self.messages.append(query_wrapper)
        # Initialize a response variable
        data = None

        # Retry mechanism for robustness
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=self.messages
                )
            
                # Extracting data from the response
                data = response.choices[0].message.content
                break  # Exit the loop if the query is successful

            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)  # Wait for 1 second before retrying (adjust as needed)
        
        return data
    

    def gpt_4(self, prompt, max_retries=5):
        # Setup for entering into messages
        query_wrapper = {"role": "user", "content": f"{prompt}"}
        self.messages.append(query_wrapper)
        # Initialize a response variable
        data = None

        # Retry mechanism for robustness
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=self.messages
                )
            
                # Extracting data from the response
                data = response.choices[0].message.content
                break  # Exit the loop if the query is successful

            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)  # Wait for 1 second before retrying (adjust as needed)
        return data
    


    def gpt_json(self, prompt, data, example, model="gpt-3.5-turbo-0125", max_retries=5):
        # Setup for entering into messages
        query_wrapper = {"role": "user", "content": f"{prompt}\n[data]```{data}\n This is the json format you will use\n[format]\n```{example}```"}
        self.messages.append(query_wrapper)
        # Initialize a response variable
        data = None

        # Retry mechanism for robustness
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=self.messages,
                    response_format={ "type": "json_object" }
                )
            
                # Extracting data from the response
                data = response.choices[0].message.content
                
                break  # Exit the loop if the query is successful

            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)  # Wait for 1 second before retrying (adjust as needed)
        self.reset_messages() 
        return data
    



    def gpt_url_vision(self, query, image_url, max_tokens=4096, max_retries=5):
        data = None

        # Retry mechanism for robustness
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{query}"},
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                        },
                    ],
                    }
                ],
                max_tokens=max_tokens,
                )
                data = response.choices[0].message.content
                break  # Exit the loop if the query is successful

            except Exception as e:
                print(f"An error occurred: {e}. Attempt {attempt + 1} of {max_retries}.")
                time.sleep(1)  # Wait for 1 second before retrying (adjust as needed)
        self.reset_messages() 
        return data
    
    

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')



    def gpt_vision(self, query, image_path, max_tokens=4096, max_retries=5):
        
        # Getting the base64 string
        base64_image = self.encode_image(image_path)

        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": query
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": max_tokens
        }
        retry_counter = 0
        while True:
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                data = response.json()
                # print(f"GPT Response:  {data}")
                text = data['choices'][0]['message']['content']

                return text
            
            except Exception as e:
                retry_counter += 1
                if retry_counter > 4:
                    return data
                
                print("There was an error with GPT Vision")
                print(data)
                print(data['error']['code'])
                if 'rate limit' in data['error']['code']:
                    print("Waiting 30 seconds to retry against rate limit")
                    time.sleep(30)



    def transcribe_audio(self, audiofile):
        with open(audiofile, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format='text'
            )
        return transcript
    
    
    def speak(self, text, voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], filename="speech.mp3"):
        """
            Speak text that is input into the function.

            Args:
            voice (str): The option for the function, which can be either 'alloy', 'echo', 'fable', 'onyx', 'nova' or 'shimmer'.
            """
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = self.client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text
        )

        response.stream_to_file(speech_file_path)

        return speech_file_path
    


    def get_embeddings(self, text):
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        return embedding
    