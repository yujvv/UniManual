from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import os
# import langid
import deepl
from openai import OpenAI
from api.chunkingText import TextCutter
from api.rag_class import RagInterface
from api.action_index import ActionSemanticRetriever


app = Flask(__name__)
CORS(app)

# OpenAI Settings
api_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=api_key)
cutter = TextCutter(min_chars=11)
rag_processor = RagInterface('demo.docx', 'index0', './index')

auth_key = os.getenv('DEEPL_KEY')
translator = deepl.Translator(auth_key)


templates = {
    'ZH': '请扮演一个智能助手，基于背景，使用中文，简练且严谨地回答问题。',
    'JA': '背景に基づいて、日本語を使用して、簡潔かつ正確に質問に答えるインテリジェントアシスタントを演じてください。',
    'EN': 'Please act as an intelligent assistant, using English, and answer questions concisely and accurately based on the background.'
}

folder_path = "../extracted_images"
# global images_list
# file_list = os.listdir(folder_path)
image_list = [os.path.splitext(filename)[0] for filename in os.listdir(folder_path)]

@app.route('/')
def hello():
    return "hello"

def generate_text_stream(prompt, language):
    
    template = templates.get(language, 'Please act as an intelligent assistant and answer questions concisely and accurately based on the background.')
    
    for chunk in client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {'role': 'system', 'content': template},
            {'role': 'user', 'content': prompt},
        ],
        stream=True
    ):
        if (text_chunk := chunk.choices[0].delta.content):
            # print("Response of chatgpt:", text_chunk)
            yield text_chunk



@app.route('/process_text', methods=['POST'])
def process_audio():
    print("Request form:")
    print(request.form)

    if 'text' not in request.form:
        return jsonify({'error': 'No text in request'}), 400

    transcription = request.form['text']
    print("Transcript:", transcription)
    
    # 如果DeepL速度慢，可以考虑换ASR模型直接翻译
    language = request.form['language']
    main_lang = "ZH"
    if language != main_lang:
        translation_result = translator.translate_text(transcription, target_lang=main_lang)
        print("Translated Transcript:", translation_result.text)
        transcription = translation_result.text
    
    # DeepL也能做语言类型识别
    # lang, _ = langid.classify(transcription)
    # print("Language:", lang)

    prompt, title = rag_processor.process_input(transcription, language)
    
    if title not in image_list:
        print("__________", image_list)
        title = 'N'
    
    def response_stream():
        # yield f"Detected Language: {lang}\n\n"
        yield f"{title} |"
        # yield from cutter.cut_text(generate_text_stream(transcription))
        for chunk in cutter.cut_text(generate_text_stream(prompt, language)):
            print(f"Chunk sent: {chunk}")
            yield chunk

    return Response(response_stream(), content_type='text/plain')


# 我会将这些中文的部分全部转化为向量，然后用被识别的text和这些内容进行相似性搜索，召回序号，从而对这些text进行感情分类识别

actions_semantics = {
    # Tear (悲伤)
    1: [
        "悲伤",
        "心如刀绞 痛苦不堪",
        "泪流满面 悲伤欲绝",
        "情绪低落 万念俱灰",
        "伤心难过 黯然神伤",
        "哀恸不已 悲痛欲绝"
        # "我感到很难过",
        # "这件事让我伤心",
        # "我有点沮丧",
        # "我非常悲伤",
        # "我觉得很郁闷",
        # "我的心情很低落",
        # "我快要哭了",
        # "我感到非常失落",
        # "我内心充满了悲伤",
        # "我不是很开心，但也不至于特别难过",
        # "虽然有点伤心，但我会坚强面对",
        # "这个消息让我很受打击",
        # "我的心情跌到了谷底",
        # "我感觉世界都灰暗了"
    ],
    # Angry (愤怒)
    2: [
        "愤怒",
        "怒火中烧 暴跳如雷",
        "气愤填膺 怒不可遏",
        "勃然大怒 火冒三丈",
        "恼羞成怒 怒气冲天",
        "义愤填膺 愤怒至极"
    ],
    # Despair (绝望)
    3: [
        "绝望",
        "绝望无助 万念俱灰",
        "心如死灰 绝望至极",
        "山穷水尽 绝望无望",
        "陷入绝境 无计可施",
        "绝望崩溃 生无可恋"
    ],
    # Happy (快乐)
    4: [
        "快乐",
        "欣喜若狂 乐不可支",
        "喜笑颜开 心花怒放",
        "兴高采烈 欢欣鼓舞",
        "雀跃不已 欢天喜地",
        "幸福快乐 喜不自胜"
    ],
    # Shock (震惊)
    5: [
        "震惊",
        "震惊不已 目瞪口呆",
        "大吃一惊 震撼至极",
        "惊骇万分 难以置信",
        "震惊愕然 瞠目结舌",
        "惊诧莫名 心神不定"
    ]
}


retriever = ActionSemanticRetriever(actions_semantics)

@app.route('/get_action', methods=['POST'])
def get_action():
    data = request.json
    text_chunk = data.get('chunk')
    
    if not text_chunk:
        return jsonify({"error": "No text chunk provided"}), 400

    # 检索相关动作
    relevant_actions = retriever.query_actions(text_chunk)
    
    for action, semantic, score in relevant_actions:
        print(f'Action: {action}, Semantic: {semantic}, Score: {score}')

    if not relevant_actions or relevant_actions[0][2] < 0.3:
        return jsonify({"action": 0}), 200
    
    # 只返回动作编号，不包含分数
    return jsonify({"action": relevant_actions[0][0]}), 200

    # if not relevant_actions or relevant_actions[0][2] < 0.15:
    #     return jsonify({"action": 0, "score": 0}), 200
    
    # return jsonify({"action": relevant_actions[0][0], "score": float(relevant_actions[0][2])}), 200


if __name__ == '__main__':
    app.run(debug=False, port=8080)
    # app.run(debug=False, host='0.0.0.0', port=8080)
    # app.run(debug=False, host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
