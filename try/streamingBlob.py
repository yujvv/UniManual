from flask import Flask, request, Response, jsonify
from RealtimeTTS import TextToAudioStream, AzureEngine
import io
import langid
from flask_cors import CORS
from pydub import AudioSegment
from openai import OpenAI

AudioSegment.converter = "D:/ffmpeg-7.0.1-full_build/bin/ffmpeg.exe"

app = Flask(__name__)
CORS(app)

# Azure Settings
azure_key = ""
azure_region = "japaneast"

# OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)

def generate(prompt):
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        if (text_chunk := chunk.choices[0].delta.content):
            print("Response of chatgpt", text_chunk)
            yield text_chunk

def text_start():
    print("[TEXT START]", end="", flush=True)

def text_stop():
    print("[TEXT STOP]", end="", flush=True)

def audio_start():
    print("[AUDIO START]", end="", flush=True)

def audio_stop():
    print("[AUDIO STOP]", end="", flush=True)

def transcribe(client, request):
    if 'audio' in request.files:
        audio_data = request.files['audio']
        audio_bytes = audio_data.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        output_path = "output.wav"
        audio_segment.export(output_path, format="wav")
        audio_file = open("output.wav", "rb")

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    else:
        raise ValueError("Invalid audio data format")

    return transcript

def streamingTTS(text, lang):
    if lang == "zh":
        azure_voice = "zh-CN-XiaoxiaoNeural"
    elif lang == "ja":
        azure_voice = "ja-JP-NanamiNeural"
    else:
        azure_voice = "en-US-AriaNeural"

    azure_engine = AzureEngine(azure_key, azure_region, voice=azure_voice)
    stream = TextToAudioStream(
        azure_engine,
        on_text_stream_start=text_start,
        on_text_stream_stop=text_stop,
        on_audio_stream_start=audio_start,
        on_audio_stream_stop=audio_stop,
        language=lang,
        log_characters=True
    )

    def on_audio_chunk_callback(chunk):
        print(f"Chunk received, len: {len(chunk)}")
        yield chunk

    stream.feed(generate(text))
    # stream.play_async(tokenizer="stanza", language=lang, on_audio_chunk=on_audio_chunk_callback, muted=True)
    stream.play_async(language=lang, on_audio_chunk=on_audio_chunk_callback, muted=True)

    while stream.is_playing():
        continue

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file in request'}), 400

    result = transcribe(client, request)
    transcription = result.text
    print("Transcript:", transcription)

    lang, _ = langid.classify(transcription)
    print("Language:", lang)

    return Response(streamingTTS(transcription, lang), mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)