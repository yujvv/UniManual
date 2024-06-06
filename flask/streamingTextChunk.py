from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import io
import os
# import langid
from openai import OpenAI
from chunkingText import TextCutter
from rag_class import RagInterface
import deepl

AudioSegment.converter = "D:/ffmpeg-7.0.1-full_build/bin/ffmpeg.exe"

app = Flask(__name__)
CORS(app)

# OpenAI Settings
api_key = ""
client = OpenAI(api_key=api_key)
cutter = TextCutter(min_chars=11)
rag_processor = RagInterface('demo.docx', 'index0', './index')

auth_key = ""
translator = deepl.Translator(auth_key)


templates = {
    'ZH': '请扮演一个智能助手，基于背景，使用中文，简练且严谨地回答问题。',
    'JA': '背景に基づいて、日本語を使用して、簡潔かつ正確に質問に答えるインテリジェントアシスタントを演じてください。',
    'EN': 'Please act as an intelligent assistant, using English, and answer questions concisely and accurately based on the background.'
}

folder_path = "../extracted_images"
# global images_list
# file_list = os.listdir(folder_path)
image_list = [os.path.splitext(filename)[0] for filename in os.listdir(folder_path)]


def generate_text_stream(prompt, language):
    
    template = templates.get(language, 'Please act as an intelligent assistant and answer questions concisely and accurately based on the background.')
    
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {'role': 'system', 'content': template},
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
    
    # 如果DeepL速度慢，可以考虑换ASR模型直接翻译
    language = request.form.get('language')
    main_lang = "ZH"
    if language != main_lang:
        translation_result = translator.translate_text(transcription, target_lang=main_lang)
        print("Translated Transcript:", translation_result.text)
        transcription = translation_result.text
    
    # DeepL也能做语言类型识别
    # lang, _ = langid.classify(transcription)
    # print("Language:", lang)

    prompt, title = rag_processor.process_input(transcription, language)
    
    if title not in image_list:
        print("__________", image_list)
        title = 'N'
    
    def response_stream():
        # yield f"Detected Language: {lang}\n\n"
        yield f"{title} |"
        # yield from cutter.cut_text(generate_text_stream(transcription))
        for chunk in cutter.cut_text(generate_text_stream(prompt, language)):
            print(f"Chunk sent: {chunk}")
            yield chunk

    return Response(response_stream(), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
