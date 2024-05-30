from RealtimeTTS import TextToAudioStream, AzureEngine
import time
from openai import OpenAI

# Azure Settings
azure_key = ""
azure_region = "japaneast"

# OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)

# Language settings
language = "zh-CN"  # Change to "en-US" for English or "ja-JP" for Japanese
if language == "zh-CN":
    azure_voice = "zh-CN-XiaoxiaoNeural"
elif language == "ja-JP":
    azure_voice = "ja-JP-NanamiNeural"
else:
    azure_voice = "en-US-AriaNeural"

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

# Azure Engine
azure_engine = AzureEngine(azure_key, azure_region, voice=azure_voice)
azure_stream = TextToAudioStream(azure_engine, 
                           on_text_stream_start=text_start, 
                           on_text_stream_stop=text_stop, 
                           on_audio_stream_start=audio_start, 
                           on_audio_stream_stop=audio_stop,
                           log_characters=True)

prompt = "Do you think people should be tolerant to the lover or non-lover"
if language == "zh-CN":
    prompt = "您认为人们应该宽容爱人还是非爱人?三句话以内。"
elif language == "ja-JP":
    prompt = "恋人か非恋人に対して寛容であるべきかどうかについて、あなたの考えを教えてください。"

text_stream = generate(prompt)

print(f"Using language: {language}")
print("Azure Engine:")
azure_stream.feed(text_stream)
azure_stream.play_async()
while azure_stream.is_playing():
    time.sleep(0.1)