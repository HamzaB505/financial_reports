import yaml
from services.embedder import Embedder
from services.vector_db import VectorDB
from services.load_documents import load_documents
from api.query_handler import QueryHandler
from config import Config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
import os


logger = logging.getLogger("RAG")
config = Config()

load_dotenv()  # Load environment variables from .env file
CHROMA_PATH = os.environ.get("CHROMA_PATH")
FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH")
DATA_PATH = os.environ.get("DATA_PATH")
#DATA_PATH = "../../../data"


def main():
    
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
    app = FastAPI()

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Allow your Next.js frontend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    class ChatInput(BaseModel):
        message: str
