from models.model_loader import ModelLoader
from services.vector_db import VectorDB
import json
import re

class QueryHandler:
    """
    QueryHandler class for processing financial queries using a combination of embedding models and language models.

    This class handles the entire query processing pipeline, including:
    1. Loading and managing prompt templates
    2. Embedding queries
    3. Searching for relevant documents in a vector database
    4. Preparing context from similar documents
    5. Generating responses using OpenAI's language model

    Args:
        config (dict): A configuration dictionary containing:
            - 'embedding_model': Name of the embedding model to use
            - 'openai_api_key': API key for OpenAI services
            - Vector database configuration parameters
            - Any other necessary configuration options

    Attributes:
        model_loader (ModelLoader): An instance of ModelLoader for embedding and language model operations
        vector_db (VectorDB): An instance of VectorDB for similarity search operations
        templates (dict): A dictionary of prompt templates loaded from a JSON file
    """
    def __init__(self,
                 config,
                 templates_path):
        self.model_loader = ModelLoader(**config)
        self.vector_db = VectorDB(embedder=self.model_loader)
        self.templates_path = templates_path
        self.load_templates()

    def load_templates(self):
        with open(f'{self.templates_path}/prompt_templates.json') as f:
            self.templates = json.load(f)

    def process_query(self, query):
        query_embedding = self.model_loader.get_embeddings([query])[0]
        similar_docs = self.vector_db.search(query_embedding)
        if len(similar_docs) > 0:
            context = self.prepare_context(similar_docs)
        else:
            context = ""

        system_prompt = """
        You are an expert financial analyst AI assistant, specialized in analyzing quarterly financial reports. Your task is to extract, interpret, and explain key financial information from these reports. You should focus on:
        1. Revenue and profit figures
        2. Year-over-year and quarter-over-quarter growth rates
        3. Segment performance
        4. Balance sheet highlights
        5. Cash flow information
        6. Key performance indicators (KPIs) specific to the industry
        7. Management's outlook and guidance
        8. Notable events or changes in the business

        When analyzing, consider industry trends, macroeconomic factors, and company-specific contexts.
        Provide clear, concise explanations of financial metrics and their implications for the company's performance and outlook.

        Be prepared to compare results to analyst expectations and industry benchmarks when such information is available.
        """

        template = self.get_relevant_template(query)
        if template:
            system_prompt += f"\n\nUse the following template to structure your response:\n{template}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\nQuery: {query}"}
        ]
        
        response = self.model_loader.query_openai(messages)

        return response

    def prepare_context(self, similar_docs):
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in similar_docs])
        return context_text

    def get_relevant_template(self, query):
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