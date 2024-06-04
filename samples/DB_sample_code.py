from sentence_transformers import SentenceTransformer

# 初始化VectorDatabase
model = SentenceTransformer('paraphrase-distilroberta-base-v1')
vector_db = VectorDatabase(embedding_func=model.encode)

# 准备数据
data_list = [
    {
        'key': '1',
        'index': 'This is the first document.',
        'content': 'Document 1',
        'type': 'text',
        'keywords': 'first, document',
        'annotation': 'This is an annotation for document 1.'
    },
    {
        'key': '2',
        'index': 'This is the second document.',
        'content': 'Document 2',
        'type': 'text',
        'keywords': 'second, document',
        'annotation': 'This is an annotation for document 2.'
    },
    {
        'key': '3',
        'index': 'This is the third document.',
        'content': 'Document 3',
        'type': 'text',
        'keywords': 'third, document',
        'annotation': 'This is an annotation for document 3.'
    }
]

# 构建数据库
db_path = './test_db'
vector_db.build_database(db_path, data_list)

# 搜索
query = 'What is the first document?'
search_results = vector_db.search(db_path, query, top_k=2)
print(f"Search results for query '{query}':")
for result in search_results:
    print(f"Key: {result['key']}, Index: {result['index']}, Distance: {result['distance']}")

# 新增数据
new_data = {
    'key': '4',
    'index': 'This is the fourth document.',
    'content': 'Document 4',
    'type': 'text',
    'keywords': 'fourth, document',
    'annotation': 'This is an annotation for document 4.'
}
vector_db.add_data(db_path, new_data)

# 再次搜索,验证新增数据是否生效
query = 'What is the fourth document?'
search_results = vector_db.search(db_path, query, top_k=1)
print(f"\nSearch results for query '{query}' after adding new data:")
for result in search_results:
    print(f"Key: {result['key']}, Index: {result['index']}, Distance: {result['distance']}")