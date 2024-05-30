import os
from RealtimeTTS import TextToAudioStream, SystemEngine, AzureEngine, ElevenlabsEngine
# from openai import OpenAI
# import openai
from openai import OpenAI


api_key = ""
client = OpenAI(api_key=api_key)

def write(prompt: str):
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content" : prompt}],
        stream=True
    ):
        if (text_chunk := chunk["choices"][0]["delta"].get("content")) is not None:
            yield text_chunk

text_stream = write("A three-sentence relaxing speech.")

print("Starting to play", text_stream)

TextToAudioStream(SystemEngine()).feed(text_stream).play()