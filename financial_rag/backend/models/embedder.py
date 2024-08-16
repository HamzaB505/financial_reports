from transformers import AutoModel, AutoTokenizer
import torch
from tqdm import tqdm


class Embedder:

    def __init__(self, embedding_model):
        self.embedding_model = AutoModel.from_pretrained(embedding_model)
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)

    def get_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy().astype(float)

    def embed_documents(self, documents):
        output = [list(self.get_embeddings(doc).astype(float)) for doc in tqdm(documents)]

        return output

    def embed_query(self, query):
        inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
        return list(outputs.last_hidden_state.mean(dim=1).squeeze().numpy().astype(float))
