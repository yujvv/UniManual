import faiss
import pickle
import sqlite3
import os
import numpy as np

class VectorDatabase:
    def __init__(self, db_path, embedding_func):
        self.db_path = db_path
        self.embedding_func = embedding_func
        self.index_path = os.path.join(db_path, f"{os.path.basename(db_path)}.pkl")
        self.sqlite_path = os.path.join(db_path, f"{os.path.basename(db_path)}.db")
        
        os.makedirs(db_path, exist_ok=True)
        self.conn = sqlite3.connect(self.sqlite_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS metadata
                                (key TEXT PRIMARY KEY, content TEXT, type TEXT, keywords TEXT, annotation TEXT, work INTEGER)''')
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def build_database(self, data_list):
        embeddings = []
        keys = []

        for data in data_list:
            key = str(data['key'])
            index_text = data['index']
            content = data['content']
            data_type = data.get('type', '')
            keywords = data.get('keywords', '')
            annotation = data.get('annotation', '')
            work = 1 if data.get('work', True) else 0

            embedding = self.embedding_func(index_text)
            embeddings.append(embedding)
            keys.append(key)

            self.cursor.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (key, content, data_type, keywords, annotation, work))

        self.conn.commit()

        index = faiss.IndexFlatIP(len(embeddings[0]))
        index.add(np.array(embeddings))

        with open(self.index_path, 'wb') as f:
            pickle.dump((index, keys), f)

    def search(self, query, top_k=5):
        with open(self.index_path, 'rb') as f:
            index, keys = pickle.load(f)

        query_embedding = self.embedding_func(query)
        distances, indices = index.search(np.array([query_embedding]), top_k)

        results = []

        for idx, distance in zip(indices[0], distances[0]):
            key = keys[idx]
            self.cursor.execute("SELECT * FROM metadata WHERE key=?", (key,))
            row = self.cursor.fetchone()
            if row:
                result = {
                    'key': row[0],
                    'index': row[1],
                    'content': row[2],
                    'type': row[3],
                    'keywords': row[4],
                    'annotation': row[5],
                    'distance': distance
                }
                results.append(result)

        return results

    def add_data(self, data_dict):
        key = data_dict['key']
        index_text = data_dict['index']
        content = data_dict['content']
        data_type = data_dict.get('type', '')
        keywords = data_dict.get('keywords', '')
        annotation = data_dict.get('annotation', '')
        work = 1 if data_dict.get('work', True) else 0

        embedding = self.embedding_func(index_text)

        with open(self.index_path, 'rb') as f:
            index, keys = pickle.load(f)

        max_key = max([int(k) for k in keys])
        new_key = str(max_key + 1)

        index.add(np.array([embedding]))
        keys.append(new_key)

        with open(self.index_path, 'wb') as f:
            pickle.dump((index, keys), f)

        self.cursor.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (new_key, content, data_type, keywords, annotation, work))
        self.conn.commit()

    def add_index(self, data_dict):
        key = data_dict['key']
        new_index_text = data_dict['index']

        self.cursor.execute("SELECT * FROM metadata WHERE key=?", (key,))
        row = self.cursor.fetchone()

        if row:
            content = row[2]
            data_type = row[3]
            keywords = row[4]
            annotation = row[5]
            work = row[6]

            with open(self.index_path, 'rb') as f:
                index, keys = pickle.load(f)

            max_key = max([int(k) for k in keys])
            new_key = str(max_key + 1)

            embedding = self.embedding_func(new_index_text)
            index.add(np.array([embedding]))
            keys.append(new_key)

            with open(self.index_path, 'wb') as f:
                pickle.dump((index, keys), f)

            self.cursor.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (new_key, content, data_type, keywords, annotation, work))
            self.conn.commit()
            
            
# 键（key）、索引（retrieval）、文本内容（index）、内容（content）、类型（type）、关键词（Keywords）、注释（annotation）、余弦距离（distance）
# key和list的键一致；index中是一些文本，用于通过嵌入模型编码后得到的向量，作为retrieval，构建faiss数据库和进行后续的相似性搜索；content可以是任何结构和类型；当index和content完全一致的时候，type是0，其他情况type可以是任何字符串；关键词是任意字符串，注释也是任意字符串；work是布尔值，若为空则默认为true。