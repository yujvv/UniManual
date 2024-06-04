import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer


PATH = "D:/Yu/rag/bge-large-zh-v1.5"
MODEL = SentenceTransformer(PATH)

class ActionSemanticRetriever:
    def __init__(self, embedding_model, actions_semantics, index_path=None):
        self.embedding_model = embedding_model
        self.actions_semantics = actions_semantics
        self.index_path = index_path
        self.index = None

    def _load_index(self):
        if self.index_path and os.path.exists(self.index_path):
            with open(self.index_path, 'rb') as f:
                self.index = pickle.load(f)
        else:
            self.index = self._build_index()
            if self.index_path:
                with open(self.index_path, 'wb') as f:
                    pickle.dump(self.index, f)

    def _build_index(self):
        # Compute embeddings for semantics
        semantics = list(self.actions_semantics.values())
        embeddings = self.embedding_model.encode(semantics)

        # Build FAISS index
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return index

    def query_actions(self, query, k=3):
        # Load index if not loaded
        if self.index is None:
            self._load_index()

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

    def search_from_local(self, query, k=3):
        # Load embeddings and index from local file
        with open(self.index_path, 'rb') as f:
            data = pickle.load(f)
            embeddings = data['embeddings']
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)

        # Compute embedding for the query
        query_embedding = self.embedding_model.encode([query])[0]

        # Search for similar vectors in the index
        scores, indices = index.search(query_embedding.reshape(1, -1), k)

        # Return relevant actions
        relevant_actions = []
        for score, idx in zip(scores[0], indices[0]):
            action = list(self.actions_semantics.keys())[idx]
            semantic = self.actions_semantics[action]
            relevant_actions.append((action, semantic, score))

        return relevant_actions

# Example usage
actions_semantics = {
    'open_file': 'Open a file in the current directory',
    'save_file': 'Save the current file with a new name',
    'search_text': 'Search for specific text within the file',
    'replace_text': 'Replace text in the file with new text',
    # Add more actions and semantics here
}

# Assume you have an embedding model instance
embedding_model = MODEL

index_path = 'index.pkl'  # Path to store/load the index

retriever = ActionSemanticRetriever(embedding_model, actions_semantics, index_path)

# Query actions (load index into memory)
query = 'Find and replace specific text in a file'
relevant_actions = retriever.query_actions(query)
for action, semantic, score in relevant_actions:
    print(f'Action: {action}, Semantic: {semantic}, Score: {score}')

# Search actions from local file (without loading index into memory)
# query = 'Open a file in the current directory'
# relevant_actions = retriever.search_from_local(query)
# for action, semantic, score in relevant_actions:
#     print(f'Action: {action}, Semantic: {semantic}, Score: {score}')


