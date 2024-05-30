from openai import OpenAI
api_key = ""
client = OpenAI(api_key=api_key)

audio_file= open("Keira.wav", "rb")

transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)

# 官方指南
# https://platform.openai.com/docs/guides/speech-to-text/improving-reliability