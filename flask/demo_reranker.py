import streamlit as st
import time
import os
import random
from api.faiss_api import Faiss_GPU
from api.loader_docx import Loader
from api.chatglm import ChatGLMInterface
from api.reranker_index import RerankerIndex

# import logging
# logging.getLogger('streamlit').setLevel(logging.ERROR)

# Function to build dictionary from content list
def build_dict(content_list):
    result_dict = {}
    title_dict = {}
    for item in content_list:
        result_dict[item["content"]] = item["index"]
        title_dict[item["content"]] = item["title"]
    # 输出的两个字典，key都是text chunking本身，value分别为index和title
    return result_dict, title_dict

# Function to initialize models
@st.cache_resource()
def initialize_models():
    loader = Loader()
    docx_file = 'M9Z.docx'
    content_list = loader.extract_content(docx_file)
    result_dict, title_dict = build_dict(content_list)
    faiss_gpu = Faiss_GPU("demo00zz", "./index")
    faiss_gpu.add(result_dict)
    language_model_interface = ChatGLMInterface()
    reranker = RerankerIndex()
    return faiss_gpu, result_dict, title_dict, language_model_interface, reranker

# Set the page configuration
st.set_page_config(
    page_title="Q&A Interface",
    page_icon=":question:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Add some CSS styles
css = """
<style>
h1 {
    font-family: 'Helvetica Neue', sans-serif;
    font-weight: bold;
    color: #333333;
}
.input-area {
    padding: 20px;
    background-color: #f5f5f5;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.output-area {
    padding: 20px;
    background-color: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Add a header
st.markdown("<h1>🔍 Car 🚗 Q&A Interface </h1>", unsafe_allow_html=True)

# Initialize the chat history
chat_history = []

# Initialize models
faiss_gpu, result_dict, title_dict, language_model_interface, reranker = initialize_models()

# Function to display images
# def display_images(image_title):
#     st.image("{image_title}.png", caption=image_title, use_column_width=True)
def display_images(image_title, score):
    image_path = f"extracted_images/{image_title}.png"
    # if os.path.exists(image_path) and score > 0.7:
    if os.path.exists(image_path) and score > 0.5:
        st.image(image_path, caption=image_title, use_column_width=True)
    else:
        st.write(f"⛔️ No 📷 Image.")
        # You can display a default placeholder image here if you want
        # st.image("placeholder.png", caption="Placeholder", use_column_width=True)


def get_random_response():
    responses = [    
        "哎呀，对不起哦，我找不到相关信息。你可以给我更多细节吗？或者试试别的查询呢？",    
        "抱抱~我没找到你需要的信息。要不要换个关键词或者再详细描述一下你的需求呢？",    
        "呜呜，对不起，我没找到相关内容。你能不能提供更多具体的细节？或者问我其他问题也可以哦~",    
        "很抱歉，我没找到你要的信息。如果还有其他问题或者需要更多帮助，随时告诉我哦~",    
        "哦不，我没能找到你需要的资料。如果有其他问题或者需要特别的帮助，告诉我吧，我会尽力帮你的~"]

    
    return random.choice(responses)

# Add an input area
with st.form("input_form"):
    user_input = st.text_area("Enter your question:", height=200)
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        # Add the user input to the chat history
        chat_history.append(("User", user_input))

        # Process the user input and generate the output
        results = faiss_gpu.query_index(user_input, result_dict, title_dict)

        # 提取每一行的第一个元素
        chunkingList = [row[0] for row in results]
        reIndex = reranker.find_most_similar_index(user_input, chunkingList)
        top = results[reIndex][0]
        title = results[reIndex][3]
        # prompt = f"你好，你是我的车内助手。请基于背景，帮我温柔地回答问题。\nContext:{top}\nQ: {user_input}\nA:"

        prompt = (
            f"请你扮演一个专业的车辆助手，基于以下背景信息，简短且真实地回答我的问题。\n\n"
            f"### 背景信息:\n{top}\n\n"
            f"### 用户问题:\n{user_input}\n\n"
            f"### 请注意：请确保你的问题与提供的背景信息相关。如果背景信息无法解答你的问题，请提供更清晰的问题描述。"
        )
        # prompt = (
        #     f"你好呀，Uni！请你扮演一个可爱俏皮且专业的女孩，基于以下背景信息，详细且温柔地回答我的问题哦~\n\n"
        #     f"### 背景信息:\n{top}\n\n"
        #     f"### 用户问题:\n{user_input}\n\n"
        #     f"### 请针对问题，给出详细且有帮助的回答："
        # )

        output = language_model_interface.generate_response(prompt, False)

        score = results[reIndex][2]
        hint = ""
        if score > 0.5:
            hint = "(知识来源于《" + title + "》章节)"
        else:
            hint = "(提供的背景中没有相关的知识)"
        bot = output + hint
        print("\nScore_______", score)
        print("Title_______", title)

        # Add a typing animation
        typing_animation = st.empty()
        for i in range(3):
            typing_animation.write(".")
            time.sleep(0.1)
        typing_animation.empty()

        display_images(title, score)

        # Add the output to the chat history
        chat_history.append(("Bot", bot))

        # Clear the input area
        user_input = ""

# Display the chat history
for sender, message in chat_history:
    if sender == "User":
        st.markdown(f"<div class='input-area'><strong>You:</strong> {message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='output-area'><strong>Bot:</strong> {message}</div>", unsafe_allow_html=True)
