from models.model_loader import LLMModels
from models.embedder import Embedder
from config import Config
from util.utils import extract_info_from_query
from upstash_vector import Index

from langchain_community.vectorstores.chroma import Chroma
import json
import re
from dotenv import load_dotenv
import os
import logging


load_dotenv()


class QueryHandler:
    """
    """
    def __init__(self):
        self.llm = LLMModels()
        self.embedder = Embedder()
        
        self.index = Index(url=os.environ["UPSTASH_VECTOR_REST_URL"],
                           token=os.environ["UPSTASH_VECTOR_REST_TOKEN"])
    
    
    def enrich_query_metadata(self, query, query_metadata):
        logging.info(self.index)
        name_spaces = self.index.list_namespaces()
        print("name spaces found")
        print(name_spaces)

        # regex can be a bitch sometimes and not recognize the company name
        if query_metadata["company"] is not None:
            wanted_company = [name for name in name_spaces if query_metadata["company"] in name][0]
        else:
            # brute force that mf
            ## list of all companies we have
            companies_found = [c for c in ["berkshire hathaway", "tesla", "alphabet", "exxonmobil"] if c in query]
            print(companies_found)
            for name in name_spaces:
                # ignore the default namespace cuz we dont use it
                if name!="":
                    av_name_space = name.split("_")[0].lower()
                    query_company = companies_found[0].split(" ")[0].lower()
                    if query_company in av_name_space:
                        wanted_company = name 
        return wanted_company

    def query_db(self, query, query_metadata):

        wanted_company = self.enrich_query_metadata(query, query_metadata)
        print(wanted_company)
        vector = self.embedder.embedding_model.get_query_embedding(query)
        logging.info(f"""DB company namespace: {wanted_company} & {query_metadata["company"]}""")
        query_conf = {"vector": vector, 
                      "top_k": 5,
                      "include_vectors": False,
                      "include_metadata": True,
                      "include_data": True,
                      "namespace": wanted_company,
                      }
        metadata_filter = ""
        if query_metadata["year"] is not None:
            metadata_filter = f"""year = '{query_metadata["year"]}'"""
        if query_metadata["quarter"] is not None:
            metadata_filter = metadata_filter+" AND "+f"""quarter == '{query_metadata["quarter"]}' """
        query_conf["filter"] = metadata_filter
        #"filter": "year = '' AND quarter = '1st'"
        similar_docs = self.index.query(**query_conf)
        
        print(similar_docs)
        return similar_docs
    
    
    def rag_query(self, query):
        query = query.lower()
        # to be used in querying database
        query_metadata = extract_info_from_query(query)
        logging.info(query_metadata)
        print("inside rag_query")
        similar_docs = self.query_db(query,
                                     query_metadata)
        print("after query")
        if len(similar_docs) > 0:
            context = self.prepare_context(similar_docs)
        else:
            context = ""
        print(context)
        #template = self.get_relevant_template(query)
        
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
        context_text = "\n\n---\n\n".join([doc.data for doc in similar_docs])
        print([doc.metadata["source"] for doc in similar_docs])
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