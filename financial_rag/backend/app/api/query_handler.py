from models.model_loader import ModelLoader
from database.vector_db import VectorDB

class QueryHandler:
    def __init__(self, config, vector_db):
        self.model_loader = ModelLoader(config)
        self.vector_db = vector_db

    def process_query(self, query):
        query_embedding = self.model_loader.get_embeddings(query)
        similar_docs = self.vector_db.search(query_embedding)
        context = self.prepare_context(similar_docs)
        response = self.model_loader.query_openai(f"Context: {context}\nQuery: {query}")
        return response

    def prepare_context(self, similar_docs):
        # Logic to prepare context from similar documents
        pass