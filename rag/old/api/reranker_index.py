import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class RerankerIndex:
    def __init__(self, model_path = "D:/Yu/rag/bge-reranker-large"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def find_most_similar_index(self, input_string, input_list):
        pairs = [[input_string, item] for item in input_list]
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
            highest_score_idx = scores.argmax().item()
            return highest_score_idx

# Example usage:
# model_path = "D:/Yu/rag/bge-reranker-large"
# similarity_finder = RerankerIndex(model_path)
# input_string = 'what is panda?'
# input_list = ['The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.', 'hi', 'good moring']
# most_similar_index = similarity_finder.find_most_similar_index(input_string, input_list)
# print("Most similar string index:", most_similar_index)