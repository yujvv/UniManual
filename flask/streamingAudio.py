from flask import Flask, request, Response
from RealtimeTTS import TextToAudioStream, AzureEngine
import os
import openai
from openai import OpenAI
import time
from whisper import WhisperASR

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
engine = AzureEngine(os.environ.get("AZURE_SPEECH_KEY"), os.environ.get("AZURE_SPEECH_REGION"))

api_key = ""
client = OpenAI(api_key=api_key)
asr = WhisperASR(api_key)

def generate(prompt):
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content" : prompt}],
        stream=True):
        
        if (text_chunk := chunk["choices"][0]["delta"].get("content")): 
            yield text_chunk

def text_start():
    print("[TEXT START]", end="", flush=True)

def text_stop():
    print("[TEXT STOP]", end="", flush=True)

def audio_start():
    print("[AUDIO START]", end="", flush=True)
          
def audio_stop():
    print("[AUDIO STOP]", end="", flush=True)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Get the uploaded audio file
    audio_file = request.files['audio']
    
    # Process the audio using ASR (your existing code)
    # ...

    result = asr.transcribe(audio_file)
    
    print("Transcript:", result["transcript"])
    print("Language:", result["language"])
    print("Sentiment:", result["sentiment"])

    # Generate text based on the ASR output
    text = result["transcript"]
    
    # Create a TextToAudioStream instance
    stream = TextToAudioStream(engine,
                               on_text_stream_start=text_start,
                               on_text_stream_stop=text_stop,
                               on_audio_stream_start=audio_start,
                               on_audio_stream_stop=audio_stop,
                               log_characters=True)

    # Generate the text stream
    text_stream = generate(text)
    stream.feed(text_stream)
    stream.play_async()

    def audio_stream_generator():
        while stream.is_playing():
            chunk = stream.get_audio_chunk()
            if chunk:
                yield chunk
            else:
                time.sleep(0.1)

    return Response(audio_stream_generator(), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)