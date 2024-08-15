class TextCutter:
    def __init__(self, min_chars):
        self.min_chars = min_chars
        self.punctuation_chars = {',', '.', '!', '?', '，', '。', '！', '？', '；', '：', '、', '*', '＊', '——', '-', '–'}
        self.reset()

    def is_punctuation(self, char):
        return char in self.punctuation_chars

    def cut_text(self, chunk):
        self.current_block += chunk
        blocks = []

        while len(self.current_block) >= self.min_chars:
            split_index = self.min_chars
            for i in range(self.min_chars, len(self.current_block)):
                if self.is_punctuation(self.current_block[i]):
                    split_index = i + 1
                    break

            if split_index < len(self.current_block):
                blocks.append(self.current_block[:split_index].strip())
                self.current_block = self.current_block[split_index:]
            else:
                break

        return blocks

    def get_remainder(self):
        if self.current_block:
            remainder = self.current_block
            self.current_block = ""
            return remainder
        return None

    def reset(self):
        self.current_block = ""