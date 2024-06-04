import faiss
from sentence_transformers import SentenceTransformer

EMBEDDING_PATH = "D:/Yu/rag/bge-large-zh-v1.5"
model = SentenceTransformer(EMBEDDING_PATH)
# sentence_embeddings = model.encode(split_data)

class ActionSemanticRetriever:
    def __init__(self, embedding_model, actions_semantics):
        self.embedding_model = embedding_model
        self.actions_semantics = actions_semantics
        self.index = self._build_index()

    def _build_index(self):
        # Compute embeddings for semantics
        semantics = list(self.actions_semantics.values())
        embeddings = self.embedding_model.encode(semantics)

        # Build FAISS index
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index

    def query_actions(self, query, k=3):
        # Compute embedding for the query
        query_embedding = self.embedding_model.encode([query])[0]

        # Search for similar vectors in the index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)

        # Return relevant actions
        relevant_actions = []
        for score, idx in zip(scores[0], indices[0]):
            action = list(self.actions_semantics.keys())[idx]
            semantic = self.actions_semantics[action]
            relevant_actions.append((action, semantic, score))

        return relevant_actions

# Example usage
# actions_semantics = {
#     '1': 'Open a file in the current directory',
#     '2': 'Save the current file with a new name',
#     '3': 'Search for specific text within the file',
#     '4': 'Replace text in the file with new text',
#     # Add more actions and semantics here
# }

# actions_semantics = {
#     1: "强调并解释",
#     2: "详细解释",
#     3: "长时间问候",
#     4: "用左手指向前指引",
#     5: "用右手指向前指引",
#     6: "闲置",
#     7: "交给我",
#     8: "指向并引用",
#     9: "展示并指引",
#     10: "呈现选择",
#     11: "用右手指向右侧呈现",
#     12: "双手举起欢迎",
#     13: "右手指向右侧逐点解释",
#     14: "摇头否定",
#     15: "表示尊重",
#     16: "交叉双臂拒绝",
#     17: "挥动右手确认",
#     18: "点头",
#     19: "闲置25秒",
#     20: "闲置46秒"
# }

actions_semantics = {
    1: "这一点需要特别强调和解释。",
    2: "我会详细解释给你听。",
    3: "很高兴长时间问候你。",
    4: "我用左手指向前方给你指引。",
    5: "我用右手指向前方给你指引。",
    6: "暂时不做任何动作。",
    7: "交给我来处理。",
    8: "我指向并引用这一点。",
    9: "我会展示并指引你。",
    10: "这里有一些选择给你。",
    11: "我用右手指向右侧呈现给你。",
    12: "我双手举起欢迎你。",
    13: "我用右手指向右侧，逐点解释给你。",
    14: "我摇头表示否定。",
    15: "我表示尊重。",
    16: "我交叉双臂表示拒绝。",
    17: "我挥动右手表示确认。",
    18: "我点头表示同意。",
    19: "暂时不做任何动作，等待25秒。",
    20: "暂时不做任何动作，等待46秒。"
}


# Assume you have an embedding model instance
embedding_model = model

retriever = ActionSemanticRetriever(embedding_model, actions_semantics)

# query = 'Replace specific text in a file'
query = "你好，我将用右手为您指路。"
relevant_actions = retriever.query_actions(query)
for action, semantic, score in relevant_actions:
    print(f'Action: {action}, Semantic: {semantic}, Score: {score}')

# 1，chatgpt-prompt，扩展和微调description
# 2，flask接口，传入response，输出一个motion index
# 3，传入长句，按照标点符号分割，然后进行motion序列的输出，传出句子和字的起止位置。
    

# 0，重复motion+多description匹配