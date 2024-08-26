import os
import shutil
from tqdm import tqdm
from dotenv import load_dotenv

from langchain_community.vectorstores.chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class VectorDB:
    """
    VectorDB class for managing document embeddings and vector database operations.

    This class provides methods to:
    - Initialize the vector database
    - Add documents to the Chroma vector store
    - Split documents into smaller chunks
    - Create unique IDs for document chunks

    It uses an Embedder for document embedding and Chroma as the vector store.
    """
    def __init__(self,
                 embedder):
        self.embedder = embedder
        self.chroma_path = os.environ["CHROMA_PATH"]
        print(self.chroma_path)
        self.vector_db = Chroma(
                            persist_directory=self.chroma_path,
                            embedding_function=self.embedder
                        )
    def add_to_chroma(self,
                      chunks: list[Document],
                      chroma_path: str):

        logger.info('Starting embedding')

        
        logger.info("Finished embedding")
        chunks_with_ids = self.create_chunk_ids(chunks)

        #Add or Update the documents
        existing_items = self.vector_db.get(include=[]) #IDs are always included by default
        existing_ids = set(existing_items["ids"])
        logger.info(f"Number of existing documents in DB: {len(existing_ids)}")
        
        # only add documents that don't exist in the DB already
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if len(new_chunks):
            logger.info(f"👉 Adding new documents: {len(new_chunks)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            print(len(new_chunks))
            for i, chunk in tqdm(enumerate(new_chunks)):
                    logger.info(f"Adding document {i+1}/{len(new_chunks)}")
                    self.vector_db.add_documents([chunk], ids=[new_chunk_ids[i]])
            logger.info("Persisting changes...")
            self.vector_db.persist()
            logger.info("Changes persisted.")
        else:
            logger.info("✅ No new documents to add")




