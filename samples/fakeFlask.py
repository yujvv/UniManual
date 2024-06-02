from flask import Flask, Response
from flask_cors import CORS
from pydub import AudioSegment
from js import Blob

app = Flask(__name__)
CORS(app)  # 允许所有域名访问

def generate_audio_chunks(audio_file, chunk_size=16384):
    audio = AudioSegment.from_wav(audio_file)
    for i in range(0, len(audio), chunk_size):
        blob = Blob([audio[i:i+chunk_size].raw_data], type='audio/wav')
        yield blob

@app.route('/fake_audio', methods=['GET', 'POST'])
def fake_audio():
    audio_file = "Keira.wav"
    chunk_size = 16384  # 较大的块大小，以确保包含头部



    def generate():
        for chunk in generate_audio_chunks(audio_file, chunk_size):
            yield f'--boundary\r\nContent-Type: application/json\r\n\r\n{{"blob": "{chunk.base64}"}}\r\n'
        yield '--boundary--\r\n'

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=boundary')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
