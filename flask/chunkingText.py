class TextCutter:
    def __init__(self, min_chars):
        self.min_chars = min_chars
        self.punctuation_chars = {',', '.', '!', '?', '，', '。', '！', '？', '；', '：', '、', '*', '＊', '——', '-', '–'}
        self.current_block = ""
        self.block_count = 0

    def is_punctuation(self, char):
        return char in self.punctuation_chars

    def cut_text(self, text_stream):
        for char in text_stream:
            if self.is_punctuation(char):
                self.current_block += char
                self.current_block += " "
                if len(self.current_block) >= self.min_chars:
                    yield self.current_block.strip()
                    self.current_block = ""
                    self.block_count += 1
            else:
                self.current_block += char
        if self.current_block:
            yield self.current_block.strip()

# # Simulating a text stream
# def simulate_text_stream(text):
#     for char in text:
#         yield char

# # Example usage
# text_stream_en = simulate_text_stream("This is the first sentence. This is the second sentence! Is this the third sentence? Yes, it is. No, it isn't. Maybe, it could be.")
# text_stream_zh = simulate_text_stream("这是第一个句子。这是第二个句子！这是？是的，它是。不，它不是。也许，可能吧。")
# text_stream_ja = simulate_text_stream("これは最初の文です。これは2番目の文です！これは3番目の文ですか？はい、そうです。いいえ、そうではありません。たぶん、そうかもしれません。")

# cutter = TextCutter(min_chars=9)

# print("English Text Blocks:")
# for block in cutter.cut_text(text_stream_en):
#     print(block)

# print("\nChinese Text Blocks:")
# for block in cutter.cut_text(text_stream_zh):
#     print(block)

# print("\nJapanese Text Blocks:")
# for block in cutter.cut_text(text_stream_ja):
#     print(block)
