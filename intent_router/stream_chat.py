from typing import List
from openai import OpenAI
import os

class StreamChat:
    def __init__(self, system_message: str):
        self.system_message = system_message
        self.history: List[dict] = []
        api_key = os.getenv('OPENAI_KEY')
        self.client = OpenAI(api_key=api_key)

    def generate_text_stream(self, prompt: str):
        messages = [
            {'role': 'system', 'content': self.system_message},
            *self.history,
            {'role': 'user', 'content': prompt}
        ]

        full_response = ""
        for chunk in self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True
        ):
            if (text_chunk := chunk.choices[0].delta.content):
                full_response += text_chunk
                yield text_chunk

        # After generating the response, add it to the history
        self.history.append({'role': 'user', 'content': prompt})
        self.history.append({'role': 'assistant', 'content': full_response})

    def clear_history(self):
        self.history.clear()


# chat = StreamChat("You are a helpful assistant.")
# for chunk in chat.generate_text_stream("Hello, how are you?"):
#     print(chunk, end='', flush=True)
# # 清除历史
# chat.clear_history()