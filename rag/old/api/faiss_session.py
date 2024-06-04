import faiss

class SessionRetriever:
    def __init__(self, embedding_model, semantics=None):
        self.embedding_model = embedding_model
        self.semantics = semantics or {}
        self.index = self._build_index()

    def _build_index(self):
        if not self.semantics:
            return
        # Compute embeddings for semantics
        semantics = list(self.semantics.values())
        embeddings = self.embedding_model.encode(semantics)
        # Build FAISS index
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index


    # 使用IndexIVFFlat，它需要一个量化器（在这里是IndexFlatIP）来把向量映射到一个子集，从而提高搜索的效率。IndexIVFFlat允许我们在现有索引的基础上增量添加新的向量，而不需要重新构建整个索引。

    # def _build_index(self, nlist):
    #     if not self.semantics:
    #         return
    #     # Compute embeddings for semantics
    #     semantics = list(self.semantics.values())
    #     embeddings = self.embedding_model.encode(semantics)
    #     # Build FAISS index
    #     quantizer = faiss.IndexFlatIP(embeddings.shape[1])
    #     index = faiss.IndexIVFFlat(quantizer, embeddings.shape[1], nlist, faiss.METRIC_INNER_PRODUCT)
    #     index.train(embeddings)
    #     index.add(embeddings)
    #     return index

    # def update_index(self, new_semantics):
    #     if not new_semantics:
    #         return
    #     # Update semantics
    #     self.semantics.update(new_semantics)
    #     # Compute embeddings for new semantics
    #     new_semantics_list = list(new_semantics.values())
    #     new_embeddings = self.embedding_model.encode(new_semantics_list)
    #     # Add new embeddings to the existing index
    #     self.index.add(new_embeddings)

    
    def update_index(self, new_semantics):
        # Update semantics
        self.semantics.update(new_semantics)
        # Rebuild index
        self.index = self._build_index()

    def query_index(self, query, k=1):
        # Compute embedding for the query
        query_embedding = self.embedding_model.encode([query])[0]
        # Search for similar vectors in the index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
        # Return relevant actions
        relevant_actions = []
        for score, idx in zip(scores[0], indices[0]):
            action = list(self.semantics.keys())[idx]
            semantic = self.semantics[action]
            relevant_actions.append((action, semantic, score))
        return relevant_actions

# Example usage
# actions_semantics = {
#     'open_file': 'Open a file in the current directory',
#     'save_file': 'Save the current file with a new name',
#     'search_text': 'Search for specific text within the file',
#     'replace_text': 'Replace text in the file with new text',
# }

# # Assume you have an embedding model instance
# embedding_model = model
# retriever = SessionRetriever(embedding_model, actions_semantics)

# # Add new semantics
# new_semantics = {'copy_text': 'Copy selected text to clipboard'}
# retriever.update_index(new_semantics)

# query = 'Find and replace specific text in a file'
# relevant_actions = retriever.query_index(query)
# for action, semantic, score in relevant_actions:
#     print(f'Action: {action}, Semantic: {semantic}, Score: {score}')