from api.faiss_api import Faiss_GPU
from api.loader_docx import Loader
import random

class RagInterface:
    def __init__(self, docx_file, index_name, index_path):
        self.loader = Loader()
        self.content_list = self.loader.extract_content(docx_file)
        self.result_dict, self.title_dict = self._build_dict(self.content_list)
        self.faiss_gpu = Faiss_GPU(index_name, index_path)
        # 是否已构建向量数据库
        # self.faiss_gpu.add(self.result_dict)
        
        # 多语言支持
        
        self.responses = {
            'ZH': [
                "对不起，我无法找到相关信息。您可以提供更多细节吗？或者尝试其他查询？",
                "抱歉，我未找到您需要的信息。请尝试更换关键词或进一步描述您的需求。",
                "抱歉，我未能找到相关内容。请提供更多具体细节，或者询问其他问题。",
                "很抱歉，我未找到您所需的信息。如有其他问题或需要更多帮助，请随时告知。",
                "抱歉，我未能找到您需要的资料。如有其他问题或需要特别帮助，请告诉我，我会尽力协助。"
            ],
            'JA': [
                "申し訳ありませんが、関連情報が見つかりませんでした。もう少し詳しく教えていただけますか？または他の検索を試してみてください。",
                "申し訳ありませんが、ご希望の情報が見つかりませんでした。キーワードを変更するか、さらに詳細に説明してください。",
                "申し訳ありませんが、関連する内容が見つかりませんでした。具体的な詳細を提供するか、他の質問をしてください。",
                "申し訳ありませんが、ご希望の情報が見つかりませんでした。他に質問がある場合や、さらにサポートが必要な場合はお知らせください。",
                "申し訳ありませんが、ご希望の資料が見つかりませんでした。他に質問がある場合や特別なサポートが必要な場合はお知らせください。できる限りお手伝いします。"
            ],
            'EN': [
                "Sorry, I couldn't find the relevant information. Could you provide more details or try another query?",
                "Sorry, I couldn't find the information you need. Please try changing the keywords or further describe your request.",
                "Sorry, I couldn't find the relevant content. Please provide more specific details or ask another question.",
                "Sorry, I couldn't find the information you need. If you have any other questions or need more assistance, please let me know.",
                "Sorry, I couldn't find the information you need. If you have any other questions or need special assistance, please tell me, and I'll do my best to help."
            ]
        }
        
    def get_prompt(self, language, context, user_input):
        templates = {
            'ZH': (
                "你是一个智能助手，基于以下“问题”和“背景”，请生成一个简短且清晰的回答（忽略背景中 ‘[IGNORE]’ 和 ‘[/IGNORE]’ 之间的内容）。\\n\\n"
                "### 背景:\\n{context} \\n\\n"
                "### 问题:\\n{user_input}\\n\\n"
                "### 请使用中文给出简短且清晰的回答，尽可能在五句话内完成:"
            ),
            'JA': (
                "あなたはインテリジェントアシスタントです。以下の「質問」と「背景」に基づいて、簡潔で明確な回答を生成してください（背景の '[IGNORE]' と '[/IGNORE]' の間の内容は無視してください）。\\n\\n"
                "### 背景:\\n{context} \\n\\n"
                "### 質問:\\n{user_input}\\n\\n"
                "### 日本語で簡潔かつ正確に回答し、背景に基づいてください:"
            ),
            'EN': (
                "You are an intelligent assistant. Based on the following 'Question' and 'Background', please generate a concise and clear answer (ignore the content between '[IGNORE]' and '[/IGNORE]' in the background).\\n\\n"
                "### Background:\\n{context} \\n\\n"
                "### Question:\\n{user_input} \\n\\n"
                "### Please respond concisely and clearly in English, based on the context, ideally within five sentences:"
            )
        }

        return templates[language].format(context=context, user_input=user_input)

    def _build_dict(self, content_list):
        result_dict = {}
        title_dict = {}
        for item in content_list:
            result_dict[item["content"]] = item["index"]
            title_dict[item["content"]] = item["title"]
        return result_dict, title_dict

    def get_random_response(self, lang):
        response = self.responses.get(lang)
        return random.choice(response)

    def process_input(self, user_input, lang):
        results = self.faiss_gpu.query_index(user_input, self.result_dict, self.title_dict)
        if not results:
            return self.get_random_response(), False
        
        context, score, title = results[0][0], results[0][2], results[0][3]
        prompt = self.get_prompt(lang, context, user_input)
        # prompt = (
        #     f"你是一个智能助手，基于以下“问题”和“背景”，请生成一个简短且清晰的回答（（忽略背景中 ‘[IGNORE]’ 和 ‘[/IGNORE]’ 之间的内容）。\\n\\n"
        #     f"### 背景:\\n{context} \\n\\n"
        #     f"### 问题:\\n{user_input}\\n\\n"
        #     f"### 请给出简短且清晰的回答，尽可能在五句话内完成:"
        # )

        if score < 0.4:
            prompt = self.get_random_response(lang)
            title = False

        return prompt, title



# text_processor = RagInterface('M9Z.docx', 'index0', './index')
# prompt, title = text_processor.process_input(user_input)