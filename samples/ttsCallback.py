from RealtimeTTS import TextToAudioStream, ElevenlabsEngine
import time
import os

def dummy_generator():
    yield "我喜欢读书。天气很好。我们去公园吧。今天是星期五。早上好。这是我的朋友。请帮我。吃饭了吗？我在学中文。晚安。"

def on_audio_chunk_callback(chunk):
    print(f"Chunk received, len: {len(chunk)}")

engine = ElevenlabsEngine(os.environ.get("ELEVENLABS_API_KEY"))
stream = TextToAudioStream(engine).feed(dummy_generator())
stream.play_async(tokenizer="stanza", language="zh", on_audio_chunk=on_audio_chunk_callback, muted=True)

while stream.is_playing():
    time.sleep(0.1)