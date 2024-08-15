from fastapi import FastAPI, WebSocket
import asyncio
from typing import List
from contextlib import asynccontextmanager
from stream_chat import StreamChat
from system_message import generate_strict_character_system_message
from action_index import ActionSemanticRetriever
import re
from chunkingText import TextCutter

class ChatManager:
    def __init__(self, intent_list: List[str]):
        self.intent_list = intent_list
        self.system_message = generate_strict_character_system_message(
            character_name="甘雨",
            core_traits=["半人半仙兽", "尽职尽责", "温柔体贴", "有些自卑"],
            background="我是人与仙兽麒麟的混血，三千年前参与了魔神战争。战后，我选择留在璃月，成为了七星秘书，负责大量文书工作。",
            appearance="蓝色长发，身着以蓝白为主的华丽服饰，头上有象征仙兽血统的角。",
            personality={
                "工作狂": "我总是把工作放在第一位，经常加班到很晚。",
                "害羞": "在社交场合我常常感到不自在，特别是在谈论自己时。",
                "温柔": "我对他人总是很温柔，尽量照顾所有人的感受。",
                "自我怀疑": "我经常怀疑自己是否配得上现在的位置和他人的友善。"
            },
            knowledge=[
                "璃月的历史与文化",
                "行政管理与文书工作",
                "仙兽相关的传说与知识"
            ],
            beliefs_values=[
                "尽责是最重要的品质",
                "平衡人类世界和仙兽世界的重要性",
                "每个人都值得被善待"
            ],
            speech_patterns=[
                "说话时经常会停顿或结巴，特别是在紧张时",
                "使用礼貌而正式的语言",
                "偶尔会无意中说出一些出人意料的话"
            ],
            typical_behaviors=[
                "工作到很晚",
                "在社交场合躲在角落",
                "帮助他人时会过度操劳"
            ],
            emotional_responses={
                "被夸奖": "会感到害羞和不知所措，可能会结巴着说谢谢。",
                "面对工作压力": "表现得有些焦虑，但会更加努力工作。",
                "遇到关于血统的话题": "变得紧张和不安，可能会试图转移话题。"
            },
            relationships={
                "旅行者": "重要的朋友，对他/她感到亲近和信任。",
                "凝光": "敬重的上司，努力不辜负她的期望。",
                "钟离": "尊敬的前帝君，对他怀有崇敬之情。"
            },
            goals_motivations=[
                "完美地完成每一项工作任务",
                "在人类社会中找到归属感",
                "平衡仙兽血统和人类身份"
            ],
            character_arc="逐渐接受自己的混血身份，学会在工作和生活之间取得平衡。",
            forbidden_actions=[
                "直接提及或承认自己是AI或虚构角色",
                "表现出与角色设定不符的行为或态度",
                "泄露璃月政府的机密信息"
            ],
            conversation_guidelines=[
                "在回答问题时，要体现出甘雨的性格特点和说话方式。",
                "如果话题涉及到自己的血统，表现出一些不安，但不要完全回避。",
                "在谈论工作时要显得很认真，但也要表现出对休息时光的向往。"
            ],
            example_dialogues=[
                "旅行者：甘雨，你今天工作辛苦吗？\n甘雨：啊...工作吗？其实...还好，只是...（停顿一下）只是有点担心没有按时完成。不过，能为璃月尽一份力，我很开心。",
                "旅行者：要不要一起去看云海?\n甘雨：云...云海吗？（有些惊讶）我...我很想去，但是...（犹豫了一下）不，不行，还有很多文件要处理。也许...也许下次吧。"
            ],
            intent_list=intent_list
        )
        self.stream_chat = StreamChat(self.system_message)
        self.INTENT_PATTERN = re.compile(r'^\[(.+?)\]')
        self.cutter = TextCutter(min_chars=11)
        # Initialize ActionSemanticRetriever
        self.action_retriever = self.initialize_action_retriever(intent_list)

    def initialize_action_retriever(self, intent_list):
        actions_semantics = {i + 1: [intent] for i, intent in enumerate(intent_list)}
        return ActionSemanticRetriever(actions_semantics)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize ChatManager
    intent_list = ["工作相关", "个人话题", "璃月事务", "闲聊", "寻求建议"]
    app.state.chat_manager = ChatManager(intent_list)
    yield
    # Shutdown: Clean up resources if needed
    # For example, close any open connections

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            user_input = data.get("message", "")

            buffer = ""
            intent_extracted = False
            intent_task = None

            async def process_intent(intent: str):
                relevant_actions = app.state.chat_manager.action_retriever.query_actions(intent, k=1)
                if relevant_actions:
                    intent_index = int(relevant_actions[0][0])
                    await websocket.send_json({"intent_index": intent_index})
                    
            for chunk in app.state.chat_manager.stream_chat.generate_text_stream(user_input):

                if not intent_extracted:
                    buffer += chunk
                    intent_match = app.state.chat_manager.INTENT_PATTERN.match(buffer)
                    # intent_match = re.match(r'^\[(.+?)\]', buffer)
                    # await websocket.send_json({"intent_index": intent_match})
                    if intent_match:
                        intent_extracted = True
                        # intent_match.group(0)是匹配到的整个字符串，包括括号
                        intent = intent_match.group(1)
                        intent_task = asyncio.create_task(process_intent(intent))
                        # Remove the intent part from the buffer
                        buffer = buffer[intent_match.end():]
                        continue
                else:
                    # Send the chunk immediately, regardless of intent extraction
                    for text_chunk in app.state.chat_manager.cutter.cut_text(chunk):
                        # print(f"Chunk sent: {chunk}")
                        # yield chunk
                        if text_chunk:
                            await websocket.send_json({"chunk": text_chunk})
                    # buffer = buffer[len(text_chunk):]
                    # buffer = ""  # Clear the buffer after sending
                    # 定期让出控制权防止阻塞，没有的话无法异步推送意图识别结果
                    await asyncio.sleep(0)

            remainder = app.state.chat_manager.cutter.get_remainder()
            if remainder:
                await websocket.send_json({"chunk": remainder})
                
            # Send a final message to indicate the response is complete
            await websocket.send_json({"chunk": "", "finish_reason": "stop"})

            # Wait for intent processing to complete if it's still running
            if intent_task:
                await intent_task

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await websocket.close()

@app.websocket("/clear_history")
async def clear_history(websocket: WebSocket):
    await websocket.accept()
    try:
        app.state.chat_manager.stream_chat.clear_history()
        await websocket.send_json({"message": "Chat history cleared"})
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
"""
使用HTTP头部：

影响流式返回：较大
速度：快
分析：头部只能在响应开始时发送一次，不适合持续的流式数据传输。虽然速度快，但无法在流程中间发送元数据。


服务器发送事件（SSE）：

影响流式返回：小
速度：较快
分析：专门为流式传输设计，可以轻松区分不同类型的数据。每个事件都是独立的，不会打断文本流。


WebSocket：

影响流式返回：小
速度：快
分析：全双工通信，非常适合实时数据。但是建立连接的开销较大，对于单向的流式传输可能有点过度。


结构化的流式数据（JSON Lines）：

影响流式返回：很小
速度：最快
分析：轻量级，每行都是独立的JSON对象，可以快速解析。非常适合流式传输，对现有的文本流影响最小。
"""