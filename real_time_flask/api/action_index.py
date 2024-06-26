import faiss
import os
from openai import OpenAI
import numpy as np

class ActionSemanticRetriever:
    def __init__(self, actions_semantics, openai_embedding_model='text-embedding-3-small'):
        self.actions_semantics = actions_semantics
        self.openai_api_key = os.getenv('OPENAI_KEY')
        self.openai_embedding_model = openai_embedding_model
        self.client = OpenAI(api_key=self.openai_api_key)

        self.index, self.idx_to_action, self.idx_to_semantic = self._build_index()


    def get_embeddings(self, texts):
        embeddings_list = []
        for text in texts:
            text = text.replace("\n", " ")
            response = self.client.embeddings.create(
                input=text,
                model=self.openai_embedding_model
            )
            embeddings_list.append(response.data[0].embedding)
        return np.array(embeddings_list).astype(np.float32)
    
    def _build_index(self):
        semantics = []
        idx_to_action = {}
        idx_to_semantic = {}
        idx = 0
        for action, semantic_list in self.actions_semantics.items():
            for semantic in semantic_list:
                semantics.append(semantic)
                idx_to_action[idx] = action
                idx_to_semantic[idx] = semantic
                idx += 1

        # embeddings = self.embedding_model.encode(semantics)
        embeddings = self.get_embeddings(semantics)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        return index, idx_to_action, idx_to_semantic

    def query_actions(self, query, k=3):
        query_embedding = self.get_embeddings([query])[0]
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)

        relevant_actions = []
        for score, idx in zip(scores[0], indices[0]):
            action = self.idx_to_action[idx]
            semantic = self.idx_to_semantic[idx]
            relevant_actions.append((action, semantic, score))

        return relevant_actions

# 通过embedding模型处理表情注释并使用相似性搜索来实现感情分析

# actions_semantics = {
#     1: [
#         "这一点需要特别强调和解释。",
#         "我会着重讲解这部分内容。",
#         "让我来重点说明一下。"
#     ],
#     2: [
#         "我会详细解释给你听。",
#         "接下来我会逐步说明。",
#         "我来为你分解解释这个问题。"
#     ],
#     # 其他动作和语义注释，1和2代表着动作的set，鼓励同语义多动作，即多对多映射，这样更方便添加随机性。
#     # 主语言加翻译层，接下来加reranker和流处理
#     # 加感情分割，分割后再做语义检索，如果感情是nature，就在习惯的动作的set里进行随机
#     # 至此，动作可以分为  习惯的动作（无感情倾向），感情的动作（有感情倾向），每个情绪动作按照语义进行分组，然后加语义注释，（T2E后出感情分组，然后在语义数据库里进行查找，查找得到同语义的一个set，在语义set中随机）
    
#     # 明确分组的规则，然后语义生成要自动化
# }


# retriever = ActionSemanticRetriever(actions_semantics)
# while(1):
#     # query = "你好,我将用右手为您指路。"
#     query = input("输入指令______")
#     relevant_actions = retriever.query_actions(query)
#     for action, semantic, score in relevant_actions:
#         print(f'Action: {action}, Semantic: {semantic}, Score: {score}')