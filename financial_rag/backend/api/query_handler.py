from models.model_loader import LLMModels
from models.embedder import Embedder
from services.vector_db import VectorDB
from config import Config
from langchain_community.vectorstores.chroma import Chroma
import json
import re
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_community.vectorstores.upstash import UpstashVectorStore
import os
import logging
import os


load_dotenv()


class QueryHandler:
    """
    """
    def __init__(self):
        self.llm = LLMModels()
        self.embedder = Embedder(Config.embedding_model)
        
        if Config.use_chroma:
            self.vector_db = Chroma(
                            persist_directory=os.environ["CHROMA_PATH"],
                            embedding_function=self.embedder
                        )
        else:
            self.vector_db = UpstashVectorStore(embedding=True)


        print("vectordb")


    def lookup_db(self, query):

        similar_docs = self.vector_db.similarity_search_with_score(query, k=5)
        print(similar_docs)
        return similar_docs
    
    
    def rag_query(self, query):
        print("inside rag_query")
        similar_docs = self.lookup_db(query=query)
        print(similar_docs)
        print("after query")
        if len(similar_docs) > 0:
            context = self.prepare_context(similar_docs)
        else:
            context = ""
        print(context)
        #template = self.get_relevant_template(query)
        #print(template)
        template = None
        system_prompt = Config.system_prompt
        print("system prompting")
        if template:
            system_prompt += f"\n\nUse the following template to structure your response:\n{template}"
            print("used template")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context} \nQuery: {query}"}
        ]

        response = self.llm.query_model(messages)
        print(response)
        return response

    def prepare_context(self, similar_docs):
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in similar_docs])
        print([doc.metadata["source"] for doc, _score in similar_docs])
        return context_text

    def load_templates(self):
        with open(f'{Config.templates_path}/prompt_templates.json') as f:
            self.templates = json.load(f)

    def get_relevant_template(self, query):
        self.load_templates()
        print("loaded templates")
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