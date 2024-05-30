import openai
# from langdetect import detect
import langid
# from transformers import pipeline
from textblob import TextBlob
import os

class WhisperASR:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        # self.sentiment_pipeline = pipeline("sentiment-analysis")

    def transcribe(self, audio_file_path):
        with open(audio_file_path, "rb") as audio_file:
            # model_size = 'base'  # 可选值：'base', 'small', 'medium', 'large'
            response = openai.Audio.transcribe(f"whisper-1", audio_file)

        transcript = response['text']
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

# 使用示例
if __name__ == "__main__":
    api_key = ""
    asr = WhisperASR(api_key)

    audio_file_path = "Keira.wav"  # 请替换为你的音频文件路径
    result = asr.transcribe(audio_file_path)
    
    print("Transcript:", result["transcript"])
    print("Language:", result["language"])
    print("Sentiment:", result["sentiment"])
