from RealtimeTTS import TextToAudioStream, OpenAIEngine
import time
from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = ""

engine = OpenAIEngine(model="tts-1", voice="nova")

api_key = ""
client = OpenAI(api_key=api_key)

def generate(prompt):
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content" : prompt}],
        stream=True
    ):
        if (text_chunk := chunk.choices[0].delta.content): 
            yield text_chunk


def text_start():
    print("[TEXT START]", end="", flush=True)

def text_stop():
    print("[TEXT STOP]", end="", flush=True)

def audio_start():
    print("[AUDIO START]", end="", flush=True)
          
def audio_stop():
    print("[AUDIO STOP]", end="", flush=True)

stream = TextToAudioStream(engine, 
                           on_text_stream_start=text_start, 
                           on_text_stream_stop=text_stop, 
                           on_audio_stream_start=audio_start, 
                           on_audio_stream_stop=audio_stop,
                           log_characters=True)

text_stream = generate("你认为应该对家人更宽容，还是对外人更宽容？")
stream.feed(text_stream)
stream.play_async()

while stream.is_playing():
    time.sleep(0.1)


    # def audio_stream_generator():
    #     while stream.is_playing():
    #         chunk = stream.get_audio_chunk()
    #         if chunk:
    #             yield chunk
    #         else:
    #             time.sleep(0.1)

    # return app.response_class(audio_stream_generator(), mimetype='audio/wav')