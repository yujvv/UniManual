import faiss
import pickle
import sqlite3
import os
import numpy as np

class VectorDatabase:
    def __init__(self, embedding_func):
        self.embedding_func = embedding_func

    def build_database(self, db_path, data_list):
        os.makedirs(db_path, exist_ok=True)
        index_path = os.path.join(db_path, f"{os.path.basename(db_path)}.pkl")
        sqlite_path = os.path.join(db_path, f"{os.path.basename(db_path)}.db")

        embeddings = []
        keys = []

        conn = sqlite3.connect(sqlite_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS metadata
                     (key TEXT PRIMARY KEY, content TEXT, type TEXT, keywords TEXT, annotation TEXT, work INTEGER)''')

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

            c.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (key, content, data_type, keywords, annotation, work))

        conn.commit()
        conn.close()

        index = faiss.IndexFlatIP(len(embeddings[0]))
        index.add(np.array(embeddings))

        with open(index_path, 'wb') as f:
            pickle.dump((index, keys), f)

    def search(self, db_path, query, top_k=5):
        index_path = os.path.join(db_path, f"{os.path.basename(db_path)}.pkl")
        sqlite_path = os.path.join(db_path, f"{os.path.basename(db_path)}.db")

        with open(index_path, 'rb') as f:
            index, keys = pickle.load(f)

        query_embedding = self.embedding_func(query)
        distances, indices = index.search(np.array([query_embedding]), top_k)

        results = []
        conn = sqlite3.connect(sqlite_path)
        c = conn.cursor()

        for idx, distance in zip(indices[0], distances[0]):
            key = keys[idx]
            c.execute("SELECT * FROM metadata WHERE key=?", (key,))
            row = c.fetchone()
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

        conn.close()
        return results

    def add_data(self, db_path, data_dict):
        index_path = os.path.join(db_path, f"{os.path.basename(db_path)}.pkl")
        sqlite_path = os.path.join(db_path, f"{os.path.basename(db_path)}.db")

        key = data_dict['key']
        index_text = data_dict['index']
        content = data_dict['content']
        data_type = data_dict.get('type', '')
        keywords = data_dict.get('keywords', '')
        annotation = data_dict.get('annotation', '')
        work = 1 if data_dict.get('work', True) else 0

        embedding = self.embedding_func(index_text)

        with open(index_path, 'rb') as f:
            index, keys = pickle.load(f)

        max_key = max([int(k) for k in keys])
        new_key = str(max_key + 1)

        index.add(np.array([embedding]))
        keys.append(new_key)

        with open(index_path, 'wb') as f:
            pickle.dump((index, keys), f)

        conn = sqlite3.connect(sqlite_path)
        c = conn.cursor()
        c.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (new_key, content, data_type, keywords, annotation, work))
        conn.commit()
        conn.close()
        
        
    def add_index(self, db_path, data_dict):
        index_path = os.path.join(db_path, f"{os.path.basename(db_path)}.pkl")
        sqlite_path = os.path.join(db_path, f"{os.path.basename(db_path)}.db")

        key = data_dict['key']
        index_text = data_dict['index']

        conn = sqlite3.connect(sqlite_path)
        c = conn.cursor()
        c.execute("SELECT * FROM metadata WHERE key=?", (key,))
        row = c.fetchone()

        if row:
            content = row[2]
            data_type = row[3]
            keywords = row[4]
            annotation = row[5]
            work = row[6]

            embedding = self.embedding_func(index_text)

            with open(index_path, 'rb') as f:
                index, keys = pickle.load(f)

            max_key = max([int(k) for k in keys])
            new_key = str(max_key + 1)

            index.add(np.array([embedding]))
            keys.append(new_key)

            with open(index_path, 'wb') as f:
                pickle.dump((index, keys), f)

            c.execute("INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)", (new_key, index_text, content, data_type, keywords, annotation, work))
            conn.commit()

        conn.close()