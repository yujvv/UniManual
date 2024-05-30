from flask import Flask, request, send_file
import os
from tempfile import NamedTemporaryFile
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return 'No audio file found', 400

    audio_file = request.files['audio']

    # Save received audio to a temporary file
    temp_audio_file = NamedTemporaryFile(delete=False, suffix='.wav')
    audio_file.save(temp_audio_file.name)

    # Process audio (this is a dummy example, you can replace it with your own processing logic)
    audio = AudioSegment.from_wav(temp_audio_file.name)
    processed_audio = audio.reverse()

    # Save processed audio to a temporary file
    temp_processed_audio_file = NamedTemporaryFile(delete=False, suffix='.wav')
    processed_audio.export(temp_processed_audio_file.name, format='wav')

    # Return processed audio file
    return send_file(temp_processed_audio_file.name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
