from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import io
# import langid
from openai import OpenAI
from chunkingText import TextCutter
from rag_class import RagInterface

AudioSegment.converter = "D:/ffmpeg-7.0.1-full_build/bin/ffmpeg.exe"

app = Flask(__name__)
CORS(app)

# OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)
cutter = TextCutter(min_chars=15)
rag_processor = RagInterface('demo.docx', 'index0', './index')

def generate_text_stream(query):
    prompt, title = rag_processor.process_input(query)
    
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {'role': 'system', 'content': '请扮演一个智能助手，佑妮，基于背景，简练且严谨地回答问题。'},
            {'role': 'user', 'content': prompt},
        ],
        stream=True
    ):
        if (text_chunk := chunk.choices[0].delta.content):
            # print("Response of chatgpt:", text_chunk)
            yield text_chunk

def transcribe(client, request):
    if 'audio' in request.files:
        audio_data = request.files['audio']
        audio_bytes = audio_data.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        output_path = "output.wav"
        audio_segment.export(output_path, format="wav")
        audio_file = open("output.wav", "rb")
        
        # wav_io = io.BytesIO()
        # audio_segment.export(wav_io, format="wav")
        # wav_io.seek(0)

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    else:
        raise ValueError("Invalid audio data format")

    return transcript

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file in request'}), 400

    result = transcribe(client, request)
    transcription = result.text
    print("Transcript:", transcription)

    # lang, _ = langid.classify(transcription)
    # print("Language:", lang)

    def response_stream():
        # yield f"Detected Language: {lang}\n\n"
        
        # yield from cutter.cut_text(generate_text_stream(transcription))
        
        for chunk in cutter.cut_text(generate_text_stream(transcription)):
            print(f"Chunk sent: {chunk}")
            yield chunk

    return Response(response_stream(), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
