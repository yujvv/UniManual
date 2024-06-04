import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class SimilarityFinder:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def find_most_similar(self, input_string, input_list):
        pairs = [[input_string, item] for item in input_list]
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()
            highest_score_idx = scores.argmax().item()
            most_similar_string = input_list[highest_score_idx]
            return most_similar_string

# Example usage:
model_path = "D:/Yu/rag/bge-reranker-large"
similarity_finder = SimilarityFinder(model_path)
input_string = 'what is panda?'
input_list = ['The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.', 'hi', 'good moring']
most_similar = similarity_finder.find_most_similar(input_string, input_list)
print("Most similar string:", most_similar)
