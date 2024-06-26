from openai import OpenAI
# from langdetect import detect
import langid
# from transformers import pipeline
from textblob import TextBlob
import os

class WhisperASR:
    def __init__(self, api_key):
        self.api_key = api_key
        # openai.api_key = self.api_key
        self.client = OpenAI(api_key=api_key)
        # self.sentiment_pipeline = pipeline("sentiment-analysis")

    def transcribe(self, audio_file):
        
        print("______", type(audio_file))
        
        transcript = self.client.audio.transcriptions.create(
            model="whisper-1", file=audio_file.read()
        )

        # language = detect(transcript)
        language = self.detect_language(transcript)
        sentiment = self.analyze_sentiment(transcript)
        # sentiment = self.analyze_sentiment(transcript)

        return {
            "transcript": transcript,
            "language": language,
            "sentiment": sentiment
        }
    
    def detect_language(self, text):
        lang, _ = langid.classify(text)
        return lang

    # def analyze_sentiment(self, text):
    #     sentiment_result = self.sentiment_pipeline(text)
    #     return sentiment_result

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = 'positive'
        elif polarity < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        return sentiment


# if __name__ == "__main__":
#     api_key = ""
#     asr = WhisperASR(api_key)

#     audio_file_path = "Keira.wav"  # 请替换为你的音频文件路径
#     result = asr.transcribe(audio_file_path)
    
#     print("Transcript:", result["transcript"])
#     print("Language:", result["language"])
#     print("Sentiment:", result["sentiment"])
