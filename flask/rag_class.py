from flask import Flask, request, jsonify
from api.faiss_api import Faiss_GPU
from api.loader_docx import Loader
import random

class RagInterface:
    def __init__(self, docx_file, index_name, index_path):
        self.loader = Loader()
        self.content_list = self.loader.extract_content(docx_file)
        self.result_dict, self.title_dict = self._build_dict(self.content_list)
        self.faiss_gpu = Faiss_GPU(index_name, index_path)
        self.faiss_gpu.add(self.result_dict)
        # self.language_model_interface = ChatGLMInterface()

    def _build_dict(self, content_list):
        result_dict = {}
        title_dict = {}
        for item in content_list:
            result_dict[item["content"]] = item["index"]
            title_dict[item["content"]] = item["title"]
        return result_dict, title_dict

    def get_random_response(self):
        responses = [
            "对不起，我无法找到相关信息。您可以提供更多细节吗？或者尝试其他查询？",
            "抱歉，我未找到您需要的信息。请尝试更换关键词或进一步描述您的需求。",
            "抱歉，我未能找到相关内容。请提供更多具体细节，或者询问其他问题。",
            "很抱歉，我未找到您所需的信息。如有其他问题或需要更多帮助，请随时告知。",
            "抱歉，我未能找到您需要的资料。如有其他问题或需要特别帮助，请告诉我，我会尽力协助。"
        ]
        return random.choice(responses)

    def process_input(self, user_input):
        results = self.faiss_gpu.query_index(user_input, self.result_dict, self.title_dict)
        if not results:
            return self.get_random_response(), False
        
        context, score, title = results[0][0], results[0][2], results[0][3]
        prompt = (
            f"你是一个智能助手，基于以下“问题”和“背景”，请生成一个简短且清晰的回答（（忽略背景中 ‘[IGNORE]’ 和 ‘[/IGNORE]’ 之间的内容）。\\n\\n"
            f"### 背景:\\n{context} \\n\\n"
            f"### 问题:\\n{user_input}\\n\\n"
            f"### 请给出简短且清晰的回答，尽可能在五句话内完成:"
        )

        if score < 0.4:
            prompt = self.get_random_response()
            title = False

        return prompt, title



# text_processor = RagInterface('M9Z.docx', 'index0', './index')
# prompt, title = text_processor.process_input(user_input)