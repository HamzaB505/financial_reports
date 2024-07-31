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
DATA_PATH = os.environ.get("DATA_PATH")
YAML_PATH = os.environ.get("YAML_PATH")
TEMPLATES_PATH = os.environ.get("TEMPLATES_PATH")


def main():
    # Load configuration
    with open(f'{YAML_PATH}/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize components
    embedder = Embedder(config)
    vector_db = VectorDB(embedder=embedder)
    query_handler = QueryHandler(config)

    # Load and process documents
    print("Loading and processing documents...")
    documents = load_documents(DATA_PATH=DATA_PATH)
    chunks = vector_db.split_documents(documents)
    vector_db.add_to_chroma(chunks=chunks,
                            chroma_path=CHROMA_PATH)
    print("Documents loaded and processed.")

    # Test queries
    test_queries = [
        "What were the top performing sectors last quarter?",
        "Can you summarize the company's income statement?",
        "What's the current cash flow situation?",
        "How did different geographical segments perform?",
        "What are the key performance indicators and their trends?",
        "What's the management's outlook for the next quarter?"
    ]

    print("\nTesting queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = query_handler.process_query(query)
        print(f"Response: {result}")

if __name__ == "__main__":
    main()