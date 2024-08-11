import yaml
from services.embedder import Embedder
from services.vector_db import VectorDB
from services.load_documents import load_documents
from api.query_handler import QueryHandler
import logging

from dotenv import load_dotenv
import os


logger = logging.getLogger("RAG")


load_dotenv()  # Load environment variables from .env file
CHROMA_PATH = os.environ.get("CHROMA_PATH")
FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH")

DATA_PATH = os.environ.get("DATA_PATH")
#DATA_PATH = "../../../data"


def main(scrap_on=False):
    """
    This function serves as the main entry point for the financial report analysis system.
    It performs the following steps:
    1. Loads the configuration from a YAML file.
    2. Initializes key components: Scraper, Embedder, VectorDB, and QueryHandler.
    3. Scrapes financial reports using the Scraper.
    4. Embeds the scraped documents using the Embedder.
    5. Adds the embeddings to the VectorDB.
    6. Processes a sample query using the QueryHandler.

    The function demonstrates the end-to-end flow of the system, from data collection
    to query processing, showcasing how different components interact to provide
    insights from financial reports.
    """
    config_path = "C:/Users/ZENBOOK/Documents/github/financial_reports/financial_rag/backend/app/config"
    config_path = os.path.join(config_path, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    embedder = Embedder(config)
    
    vector_db = VectorDB(embedder=Embedder(config=config))

    # Create (or update) the data store.
    documents = load_documents(DATA_PATH=DATA_PATH)
    chunks = vector_db.split_documents(documents)
    #vector_db.add_to_faiss(chunks=chunks, faiss_index_path=FAISS_INDEX_PATH)
    vector_db.add_to_chroma(chunks=chunks, chroma_path=CHROMA_PATH)
    logger.info("Done loading the data")

    # Example query
    #result = query_handler.rag_query(query="What were the top performing sectors last quarter?")
    #logger.info(result)

if __name__ == "__main__":
    main()
