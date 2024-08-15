from models.model_loader import LLMModels
from models.embedder import Embedder
from services.vector_db import VectorDB
from config import Config
import json
import re
from langchain_core.output_parsers import StrOutputParser



class QueryHandler:
    """
    """
    def __init__(self,
                 templates_path):
        self.llm = LLMModels()
        self.embedder = Embedder(Config.embedding_model)
        self.vector_db = VectorDB(embedder=self.embedder)


    def lookup_db(self, query):
        query_embedding = self.embedder.get_embeddings([query])[0]
        similar_docs = self.vector_db.search(query_embedding)
        return similar_docs
    
    
    async def rag_query(self, query):
        similar_docs = self.lookup_db(query=query)

        if len(similar_docs) > 0:
            context = self.prepare_context(similar_docs)
        else:
            context = ""

        template = self.get_relevant_template(query)

        system_prompt = Config.system_prompt
        
        if template:
            system_prompt += f"\n\nUse the following template to structure your response:\n{template}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context} \nQuery: {query}"}
        ]

        response = await self.llm.query_model(messages)

        return response

    def prepare_context(self, similar_docs):
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in similar_docs])
        return context_text

    def load_templates(self):
        with open(f'{Config.templates_path}/prompt_templates.json') as f:
            self.templates = json.load(f)

    def get_relevant_template(self, query):
        self.load_templates()
        query_lower = query.lower()
        if re.search(r'income|revenue|profit|eps', query_lower):
            return self.templates.get('Income_Statement_Template')
        elif re.search(r'balance sheet|assets|liabilities|equity', query_lower):
            return self.templates.get('Balance_Sheet_Template')
        elif re.search(r'cash flow|cash from operations|free cash flow', query_lower):
            return self.templates.get('Cash_Flow_Statement_Template')
        elif re.search(r'segment|division|regional performance', query_lower):
            return self.templates.get('Segment_Performance_Template')
        elif re.search(r'kpi|key performance|metrics', query_lower):
            return self.templates.get('Key_Performance_Indicators_Template')
        elif re.search(r'outlook|guidance|forecast|future', query_lower):
            return self.templates.get('Management_Outlook_Template')
        return None