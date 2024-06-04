from flask import Flask, request, Response, jsonify
from RealtimeTTS import TextToAudioStream, AzureEngine
import os
# import openai
from openai import OpenAI
import time
import io
import langid
from flask_cors import CORS
import wave
from pydub import AudioSegment
# from whisper import WhisperASR

AudioSegment.converter = "D:/ffmpeg-7.0.1-full_build/bin/ffmpeg.exe"

app = Flask(__name__)
# 允许所有域名访问
CORS(app)
# 或者你可以只允许特定域名访问
# CORS(app, resources={r"/process_audio": {"origins": "http://localhost:3000"}})

# Azure Settings
azure_key = ""
azure_region = "japaneast"

# OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)
# asr = WhisperASR(api_key)

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

def transcribe(client, request):
    # 检查 request.files 中是否有名为 'audio' 的文件
    if 'audio' in request.files:
        audio_data = request.files['audio']
        audio_bytes = audio_data.read()
        # https://github.com/jiaaro/pydub
        # https://medium.com/@joedonovan_96143/working-with-audio-blobs-in-python-12a200972728
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        # pip install ffmpeg-downloader
        # ffdl install --add-path
        # conda install -c main ffmpeg
        
        output_path = "output.wav"
        audio_segment.export(output_path, format="wav")
        audio_file= open("output.wav", "rb")
        
        # 这个失败了
        # wav_data = io.BytesIO()
        # audio_segment.export(wav_data, format="wav")
        # wav_data.seek(0)
        
        
        # 下面的采样的方法有很大的损失
        # audio_bytes = audio_file.read()
        # # 将音频数据转换为 WAV 文件
        # wav_bytes = io.BytesIO()
        # wav_file = wave.open(wav_bytes, 'wb')
        # wav_file.setnchannels(1)  # 单声道
        # wav_file.setsampwidth(2)  # 16 位
        # wav_file.setframerate(16000)  # 16kHz 采样率
        # wav_file.writeframes(audio_bytes)
        # wav_file.close()
            
        # # 获取 WAV 文件的字节数据
        # wav_bytes.seek(0)
        # wav_data = wav_bytes.getvalue()
        
        # save_path = os.path.join('', 'recording.wav')  # 替换为您想要保存的路径和文件名
        # with open(save_path, 'wb') as f:
        #     f.write(wav_data)
      

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    # 检查 request.form 中是否有名为 'audio' 的字段
    # elif 'audio' in request.form:
    #     print("request.form___")
    #     audio_data = io.BytesIO(request.form['audio'].read())
    #     audio_data.seek(0)
    #     transcript = client.audio.transcriptions.create(
    #         model="whisper-1",
    #         file=audio_data
    #     )

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

    # Azure Engine
    azure_engine = AzureEngine(azure_key, azure_region, voice=azure_voice)
    stream = TextToAudioStream(azure_engine, 
                               on_text_stream_start=text_start, 
                               on_text_stream_stop=text_stop, 
                               on_audio_stream_start=audio_start, 
                               on_audio_stream_stop=audio_stop,language=lang,
                               log_characters=True)

    # Callback audio chunking
    def on_audio_chunk_callback(chunk):
        print(f"Chunk received, len: {len(chunk)}")
        yield chunk

    # text_stream = generate(text)
    stream.feed(generate(text))
    # stream.play_async()
    stream.play_async(tokenizer="stanza", language=lang, on_audio_chunk=on_audio_chunk_callback, muted=True)
    
    while stream.is_playing():
        continue
    
    
@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Get the uploaded audio file
    # audio_file = request.files['audio']
    
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file in request'}), 400
    
    
    # Process the audio using ASR (your existing code)
    # ...
    # https://platform.openai.com/docs/guides/speech-to-text/improving-reliability
    result = transcribe(client, request)
    transcription = result.text
    print("Transcript:", transcription)
    
    # language type
    lang, _ = langid.classify(transcription)
    print("Language:", lang)
    # print("Sentiment:", result["sentiment"])
    
    # Create a TextToAudioStream instance
    streamingAudio = streamingTTS(transcription, lang)

    return Response(streamingAudio, mimetype='audio/wav')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False, host='0.0.0.0', port=8080)