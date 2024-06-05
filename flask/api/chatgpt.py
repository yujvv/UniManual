from openai import OpenAI

class ChatGPTAssistant:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.history = []

    def generate_response(self, user_input, background_info):
        if len(self.history) > 3:
            self.history = self.history[-3:]

        prompt = (
            f"请你扮演一个专业的车辆助手，基于以下背景信息，简短且真实地回答我的问题。\n\n"
            f"### 背景信息:\n{background_info}\n\n"
            f"### 用户问题:\n{user_input}\n\n"
            f"### 请注意：要确保用户问题与提供的背景信息相关。如果背景信息无法完美解答用户问题，请促使用户提供更清晰的问题描述并基于背景信息猜测用户真正想要询问的问题（请不要提及背景信息与问题不一致的情况）。\n\n"
        )

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "请你扮演一个专业的车辆助手，基于背景信息，简短且真实地回答用户问题。"},
                {"role": "user", "content": f"{prompt}"}
            ] + self.history  # 添加历史消息
        )

        reply = completion.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": f"{reply}"})

        return reply

# 示例用法
# api_key = ''
# assistant = ChatGPTAssistant(api_key)
# user_input = "我该如何打开后备箱"
# background_info = "打开空调需要哈哈大笑"
# response = assistant.generate_response(user_input, background_info)
# print("GPT:", response)
