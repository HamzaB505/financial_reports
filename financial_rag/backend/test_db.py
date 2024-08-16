from models.embedder import Embedder
from services.vector_db import VectorDB
from services.load_documents import load_documents
from config import Config
import logging
from dotenv import load_dotenv
import os


logger = logging.getLogger("RAG")

load_dotenv()  # Load environment variables from .env file
#CHROMA_PATH = os.environ.get("CHROMA_PATH")
#DATA_PATH = os.environ.get("DATA_PATH")
DATA_PATH = "../../../data"
CHROMA_PATH = "../../../chroma"




    
vector_db = VectorDB(embedder=Embedder(embedding_model=Config.embedding_model),
                     chroma_path=CHROMA_PATH)
print(vector_db.vector_db.embeddings)
