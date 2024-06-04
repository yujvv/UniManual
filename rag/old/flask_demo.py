from flask import Flask, request, jsonify
from api.faiss_api import Faiss_GPU
from api.loader_docx import Loader
from datetime import datetime
import random
# from api.chatglm import ChatGLMInterface

app = Flask(__name__)

# Function to build dictionary from content list
def build_dict(content_list):
    result_dict = {}
    title_dict = {}
    for item in content_list:
        result_dict[item["content"]] = item["index"]
        title_dict[item["content"]] = item["title"]
    return result_dict, title_dict


# Initialize models
loader = Loader()
docx_file = 'M9.docx'
content_list = loader.extract_content(docx_file)
result_dict, title_dict = build_dict(content_list)
faiss_gpu = Faiss_GPU("index2", "./index")
faiss_gpu.add(result_dict)

# language_model_interface = ChatGLMInterface()


def get_random_response():
    # responses = [
    #     "对不起，我无法找到相关信息。您是否可以提供更多详细信息或尝试其他查询？",
    #     "抱歉，我没有找到您需要的信息。也许可以尝试不同的关键词或进一步描述您的需求。",
    #     "很抱歉，没有找到相关内容。请您提供更多具体的细节或尝试另一个问题。",
    #     "我很遗憾没有找到目标信息。如果您有其他问题或需要更多帮助，请随时告诉我。",
    #     "对不起，我无法获取到您需要的资料。如果您有其他问题或需要特定的帮助，请告知，我会尽力帮您找到答案。"
    # ]
    responses = [    
        "[NOT FOUND]哎呀，对不起哦，我找不到相关信息。你可以给我更多细节吗？或者试试别的查询呢？",    
        "[NOT FOUND]抱抱~我没找到你需要的信息。要不要换个关键词或者再详细描述一下你的需求呢？",    
        "[NOT FOUND]呜呜，对不起，我没找到相关内容。你能不能提供更多具体的细节？或者问我其他问题也可以哦~",    
        "[NOT FOUND]很抱歉，我没找到你要的信息。如果还有其他问题或者需要更多帮助，随时告诉我哦~",    
        "[NOT FOUND]哦不，我没能找到你需要的资料。如果有其他问题或者需要特别的帮助，告诉我吧，我会尽力帮你的~"
    ]


    
    return random.choice(responses)

# Function to process input and return response
def process_input(user_input):
    results = faiss_gpu.query_index(user_input, result_dict, title_dict)

    if not results:
        return get_random_response(), False
    
    context, score, title = results[0][0], results[0][2], results[0][3]

    # prompt = context

    prompt = (
        f"基于以下“问题”和“背景”，请生成一个感情丰富且简短清晰的回答。请自行判断合适的情绪语气（如愤怒、厌恶、恐惧、喜悦、中立、悲伤、惊讶），并确保回答贴合背景和问题。\n\n"
        f"### 背景:\n{context} \n（忽略背景中 ‘[IGNORE]’ 和 ‘[/IGNORE]’ 之间的内容 \n\n"
        f"### 问题:\n{user_input}\n\n"
        f"### 你是一个小女孩，佑昵。请给出感情丰富且简短清晰的回答，尽量在两到三句话内完成:"
    )

    # E.x. 用户在安装一个应用程序时遇到了问题，尝试了多种方法但均未成功。[IGNORE]问题为如何安装这个app[/IGNORE] 客服没有提供有效的解决方案。

    # prompt = (
    #     f"你好呀，Uni！请你扮演一个可爱俏皮且专业的女孩，基于以下背景信息，详细且温柔地回答我的问题哦~\n\n"
    #     f"### 背景信息:\n{context}\n\n"
    #     f"### 用户问题:\n{user_input}\n\n"
    #     f"### 请给出详细且有帮助的回答："
    # )

    # output = language_model_interface.generate_response(prompt, False)

    if score < 0.4:
        prompt = get_random_response()
        title = False

    return prompt, title

# Route for receiving text input and returning processed text and image name
@app.route('/process_text', methods=['POST'])
def process_text():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    data = request.get_json()
    user_input = data['input']

    print("Time_________", formatted_time)
    print("Input______", user_input)
    prompt, title = process_input(user_input)
    print("prompt_________", prompt, "\nTitle_________", title)

    return jsonify({'context': prompt, 'title': title})

if __name__ == '__main__':
    # app.run(debug=True)
    # 192.168.0.66
    app.run(debug=True, host='0.0.0.0', port=8080)
