from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class ActionSemanticRetriever:
    def __init__(self, reranker_model_path, actions_semantics):
        self.tokenizer = AutoTokenizer.from_pretrained(reranker_model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(reranker_model_path)
        self.model.eval()
        self.actions_semantics = actions_semantics
        self.semantics, self.idx_to_action, self.idx_to_semantic = self._prepare_data()

    def _prepare_data(self):
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
        return semantics, idx_to_action, idx_to_semantic

    def query_actions(self, query, k=3):
        pairs = [[query, semantic] for semantic in self.semantics]
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
        
        top_k_indices = scores.topk(k).indices
        
        relevant_actions = []
        for idx in top_k_indices:
            action = self.idx_to_action[idx.item()]
            semantic = self.idx_to_semantic[idx.item()]
            score = scores[idx].item()
            relevant_actions.append((action, semantic, score))

        return relevant_actions

# 示例用法
reranker_model_path = "D:/Yu/rag/bge-reranker-large"
actions_semantics = {
    1: [
        "这一点需要特别强调和解释。",
        "我会着重讲解这部分内容。",
        "让我来重点说明一下。"
    ],
    2: [
        "我会详细解释给你听。",
        "接下来我会逐步说明。",
        "我来为你分解解释这个问题。"
    ],
    # 其他动作和语义注释...
}

retriever = ActionSemanticRetriever(reranker_model_path, actions_semantics)

query = "你好,我将用右手为您指路。"
relevant_actions = retriever.query_actions(query)
for action, semantic, score in relevant_actions:
    print(f'Action: {action}, Semantic: {semantic}, Score: {score}')