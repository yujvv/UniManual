import os
import platform
from transformers import AutoTokenizer, AutoModel
# prompt格式参考
# https://www.jianshu.com/p/066631299d0e

class ChatGLMInterface:
    def __init__(self):
        self.model_path = "D:/Yu/rag/chatglm3-6b"  # 模型路径
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(self.model_path, trust_remote_code=True).half().cuda()
        self.model = self.model.eval()
        self.os_name = platform.system()
        self.clear_command = 'cls' if self.os_name == 'Windows' else 'clear'

    def generate_response(self, query: str, stop_stream: bool) -> str:
        response = ""
        current_length = 0

        # for resp in self.model.generate(self.tokenizer.encode(query, return_tensors="pt"), max_length=50, temperature=0.9, num_return_sequences=1):
        #     response = self.tokenizer.decode(resp, skip_special_tokens=True)
        #     break
        past_key_values, history = None, []
        if self.clear_command == "clear":
            past_key_values, history = None, []
        for response, history, past_key_values in self.model.stream_chat(self.tokenizer, query, history=history, top_p=1,
                                                                    temperature=0.01,
                                                                    past_key_values=past_key_values,
                                                                    return_past_key_values=True):
            if stop_stream:
                stop_stream = False
                break
            else:
                print(response[current_length:], end="", flush=True)
                current_length = len(response)

        return response

# if __name__ == "__main__":

#     language_model_interface = ChatGLMInterface()


#     while True:
#         query = input("\n用户：")
#         if query.strip() == "stop":
#             break
#         if query.strip() == "clear":
#             os.system(language_model_interface.clear_command)
#             continue

#         response = language_model_interface.generate_response(query, False)
#         print("\n模型响应：", response)
