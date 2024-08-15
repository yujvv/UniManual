class TextCutter:
    def __init__(self, min_chars):
        self.min_chars = min_chars
        self.end_punctuation = {'.', '!', '?', '。', '！', '？'}
        self.pause_punctuation = {',', '，', '；', '：', '、'}
        self.all_punctuation = self.end_punctuation.union(self.pause_punctuation)
        self.reset()

    def is_punctuation(self, char):
        return char in self.all_punctuation

    def is_end_punctuation(self, char):
        return char in self.end_punctuation

    def cut_text(self, chunk):
        self.current_block += chunk
        blocks = []

        while len(self.current_block) >= self.min_chars:
            split_index = len(self.current_block)
            last_pause_index = -1

            for i in range(self.min_chars, len(self.current_block)):
                if self.is_punctuation(self.current_block[i]):
                    if self.is_end_punctuation(self.current_block[i]):
                        split_index = i + 1
                        break
                    else:
                        last_pause_index = i + 1

            if split_index == len(self.current_block) and last_pause_index != -1:
                split_index = last_pause_index

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
        
        
"""
分割逻辑优先考虑结束标点，如果找到结束标点就立即在该处分割。
如果在最小长度之后没有找到结束标点，但找到了暂停标点，就在最后一个暂停标点处分割。
如果既没有找到结束标点也没有找到暂停标点，就保持原来的行为，在最小长度处分割

保持了最小长度的要求，确保每个分割的块至少达到最小长度
"""