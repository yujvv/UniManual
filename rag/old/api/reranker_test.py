import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_path = "D:/Yu/rag/bge-reranker-large"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

pairs = [['what is panda?', 'hi'], ['what is panda?', 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.']]
with torch.no_grad():
    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
    scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
    print("scores_______", scores)




# https://huggingface.co/BAAI/bge-reranker-v2-m3
# 常规reranker：
# 常规reranker通常是指使用传统机器学习技术（例如逻辑回归、支持向量机等）或深度学习技术（例如神经网络）来对已有的排名进行重新排序。这种reranker的目标是通过学习输入数据中的特征和排名之间的关系来改进原始排名的质量。
# 通常，常规reranker的输入特征包括各种与排名相关的信息，如文本特征、结构特征、语言模型分数等。然后，通过训练一个模型来最大化某个评价指标（如NDCG，MAP等）来学习这些特征与最终排名之间的关系。
# 基于语言模型的reranker（LLM-based reranker）：
# 基于语言模型的reranker利用预训练的语言模型（如BERT、GPT等）来对搜索结果进行重新排序。与传统reranker不同，LLM-based reranker更加注重利用语言模型对文本数据的理解能力。
# 这种reranker的工作流程通常包括以下步骤：首先，将搜索结果中的每个文档（或候选项）与查询进行拼接，形成一组文本对；然后，利用预训练的语言模型对这些文本对进行编码，得到文本对的表示；最后，通过对这些表示进行比较或计算相似度来确定最终的排名顺序。
# 基于语言模型的逐层reranker（LLM-based layerwise reranker）：
# 基于语言模型的逐层reranker是一种更加高级的reranker类型，它不仅利用了预训练的语言模型，还充分利用了语言模型的层次结构。这种reranker的目标是逐层地对搜索结果进行重新排列，以更好地捕获文本数据的各种特征和模式。
# 工作流程通常包括以下步骤：首先，将搜索结果中的每个文档（或候选项）与查询进行拼接，形成一组文本对；然后，逐层地利用预训练的语言模型对这些文本对进行编码，每一层都可以捕获不同层次的语义信息；最后，通过对每一层表示进行加权或组合，确定最终的排名顺序。


# 如下代码，我希望你帮我改写成一个类的接口，输入一个string（'what is panda?'）和一个list（['The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.', 'hi', '......']）,返回list中和string最相近的字符串。