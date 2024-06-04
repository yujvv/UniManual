# conda install faiss-cpu -c pytorch
# conda install faiss-gpu -c pytorch
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class Faiss_GPU:
    def __init__(self, name, path, embedding_model='D:/Yu/rag/bge-large-zh-v1.5'):
        self.name = name
        self.path = path
        self.embedder = SentenceTransformer(embedding_model)
        self.index_path = os.path.join(path, f"{name}.pkl")
        # self.load_or_create_index()

        self.semantics = None
        self.index = self.load_or_create_index()


    def load_or_create_index(self):
        print("Index Path:", self.index_path)
        if os.path.exists(self.index_path):
            with open(self.index_path, "rb") as f:
                index = pickle.load(f)
                # print("Existing Index:", self.index.ntotal)
                return index
        else:
            print("No Existing Index.")
            return None

    # The add method embeds the keys using the sentence transformer, checks if any of the embeddings already exist in the index, and adds the new embeddings to the index along with their corresponding indices.
    def add(self, data):
        keys = list(data.keys())
        embeddings = self.embedder.encode(keys)
        ids = np.arange(len(keys))

        if self.index is None:
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)
            for i, idx in zip(ids, range(self.index.ntotal)):
                data[keys[i]] = idx
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, "wb") as f:
                pickle.dump(self.index, f)
                print("Create Index over.")
        else:
            indices_to_add = []
            reconstructed_data = self.index.reconstruct(self.index.ntotal)
            for i, emb in zip(ids, embeddings):
                if not np.any(reconstructed_data == emb):
                    indices_to_add.append(i)
            if indices_to_add:
                self.index.add(np.array([embeddings[i] for i in indices_to_add]))
                start_idx = self.index.ntotal - len(indices_to_add)
                for i, idx in zip(indices_to_add, range(start_idx, self.index.ntotal)):
                    data[keys[i]] = idx
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                with open(self.index_path, "wb") as f:
                    pickle.dump(self.index, f)
                    print("Update Index over.")

    # The query method takes a query string as input and returns the top k most similar embeddings and their corresponding indices, along with their similarity scores.
    def query(self, query_text, k=10):
        print("Index Nums:", self.index.ntotal, " Top",k,"Result.")
        query_embedding = self.embedder.encode([query_text])[0]
        distances, indices = self.index.search(np.array([query_embedding]), k)
        return [(1 - distances[0][i], indices[0][i]) for i in range(k)]
    
    def query_index(self, query, data, title_dict, k=1):
        self.semantics = data
        # Compute embedding for the query
        query_embedding = self.embedder.encode([query])[0]
        # Search for similar vectors in the index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
        # Return relevant actions
        Retrieval = []
        for score, idx in zip(scores[0], indices[0]):
            # chunking text本身转为list，会自然和vector database中的搜索结果（index）相契合
            semantic = list(self.semantics.keys())[idx]
            keys = self.semantics[semantic]
            title = title_dict[semantic]
            Retrieval.append((semantic, keys, score, title))
        print("------------\n")
        return Retrieval

    # The delete method takes a key string as input, embeds it, checks if the embedding exists in the index, and if so, removes it from the index and saves the updated index to a pickle file.
    def delete(self, key):
        key_embedding = self.embedder.encode([key])[0]
        distances, indices = self.index.search(np.expand_dims(key_embedding, axis=0), 1)
        if indices[0] != -1:
            self.index.remove_ids(indices[0])
            with open(self.index_path, "wb") as f:
                pickle.dump(self.index, f)
                print("Index Nums after Delete:", self.index.ntotal)
        else:
            return None
        


# actions_semantics = {
#     "这一点需要特别强调和解释。": 1,
#     "我会详细解释给你听。": 2,
#     "很高兴长时间问候你。": 3,
#     "我用左手指向前方给你指引。": 4,
#     "我用右手指向前方给你指引。": 5,
#     "暂时不做任何动作。": 6,
#     "交给我来处理。": 7,
#     "我指向并引用这一点。": 8,
#     "我会展示并指引你。": 9,
#     "这里有一些选择给你。": 10,
#     "我用右手指向右侧呈现给你。": 11,
#     "我双手举起欢迎你。": 12,
#     "我用右手指向右侧，逐点解释给你。": 13,
#     "我摇头表示否定。": 14,
#     "我表示尊重。": 15,
#     "我交叉双臂表示拒绝。": 16,
#     "我挥动右手表示确认。": 17,
#     "我点头表示同意。": 18,
#     "暂时不做任何动作，等待25秒。": 19,
#     "暂时不做任何动作，等待46秒。": 20
# }



# faiss_gpu = Faiss_GPU("my_index", "./text/test")

# # Add some data
# # faiss_gpu.add(actions_semantics)

# # Query for similar items

# results = faiss_gpu.query_index("你好，我将用右手为您指路。", actions_semantics)


# for action, semantic, score in results:
#     print(f'Action: {action}, Semantic: {semantic}, Score: {score}')

# print(results)  # [(0.8, 0), (0.7, 1), (0.6, 2)]

# # Delete an item
# faiss_gpu.delete("apple")
        



# 关于faiss-gpu
# 我希望你能仔细学习faiss的开发指示，帮助我构建一系列python的api，关于faiss-gpu。
# 具体有如下函数功能：
# 传入两个参数，name和path，维护一个本地的pkl的faiss向量数据库，如果对应path的{name}.pkl不存在，就新建一个faiss向量数据库，否则加载为类变量。
# 添加：传入一个字典，key是一串字符串，而velue是一个index。调用作为参数传入的embedding模型（SentenceTransformer初始化后的），将key进行embedding处理后得到embedding key，将其更新到faiss向量数据库中；如果已经有了完全一致的embedding key，那么返回null，否则加到原有的faiss向量数据库。
# 查询：传入一个query（字符串类型），通过embedding处理后，在faiss的向量数据库中寻找最相近的前k个embedding key，返回这k个的相似分数以及其对应index。
# 删除：传入一个key，是一串字符串，经过embedding处理后，得到embedding key，查询faiss向量数据库中是否有完全相似的embedding key，若有，则删除这个item并更新faiss向量数据库，否则返回null。