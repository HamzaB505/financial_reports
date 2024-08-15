from models.embedder import Embedder
from services.vector_db import VectorDB
from services.load_documents import load_documents
from config import Config
import logging
from dotenv import load_dotenv
import os


logger = logging.getLogger("RAG")

load_dotenv()  # Load environment variables from .env file
CHROMA_PATH = os.environ.get("CHROMA_PATH")
DATA_PATH = os.environ.get("DATA_PATH")
#DATA_PATH = "../../../data"


def main():
    
    vector_db = VectorDB(embedder=Embedder(embedding_model=Config.embedding_model))

    # Create (or update) the data store.
    documents = load_documents(DATA_PATH=DATA_PATH)
    chunks = vector_db.split_documents(documents)
    vector_db.add_to_chroma(chunks=chunks, chroma_path=CHROMA_PATH)
    logger.info("Done loading the data")



if __name__ == "__main__":
    logger.info("Initializing database: CHROMA version")
    main()
    logger.info("Done creating VectorDB: CHROMA version")
