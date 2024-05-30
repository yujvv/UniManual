from RealtimeTTS import TextToAudioStream, AzureEngine
import time
from openai import OpenAI

# only English
engine = AzureEngine(os.environ.get("AZURE_SPEECH_KEY"), os.environ.get("AZURE_SPEECH_REGION"))

api_key = ""
client = OpenAI(api_key=api_key)

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

stream = TextToAudioStream(engine, 
                           on_text_stream_start=text_start, 
                           on_text_stream_stop=text_stop, 
                           on_audio_stream_start=audio_start, 
                           on_audio_stream_stop=audio_stop,
                           language='zh',
                           fast_sentence_fragment=True,
                        #    the method will prioritize speed, generating and playing sentence fragments faster. This is useful for applications where latency matters.
                           minimum_sentence_length =3,
                        #    Sets the minimum character length to consider a string as a sentence to be synthesized. This affects how text chunks are processed and played.
                           log_characters=True)

text_stream = generate("Do u think people should be tolerant to the lover or non-lover")
stream.feed(text_stream)
stream.play_async()

while stream.is_playing():
    time.sleep(0.1)


    # def audio_stream_generator():
    #     while stream.is_playing():
    #         chunk = stream.get_audio_chunk()
    #         if chunk:
    #             yield chunk
    #         else:
    #             time.sleep(0.1)

    # return app.response_class(audio_stream_generator(), mimetype='audio/wav')