# pip install text2emotion
import text2emotion as te

# 输入文本
text = "I am feeling very happy today because I got a new job!"

# 分析文本情感
emotions = te.get_emotion(text)

# 打印情感分析结果
print(emotions)

# {'Happy': 1.0, 'Angry': 0.0, 'Surprise': 0.0, 'Sad': 0.0, 'Fear': 0.0}
# snownlp：一个用于中文文本处理的Python库，支持情感分析。
# jieba：一个用于中文分词的库，虽然不直接进行情感分析，但可以配合其他库使用。
# TextBlob：一个用于英文的情感分析库，也支持简单的翻译功能，结合翻译可以间接支持多语言。
# Google Alibaba API