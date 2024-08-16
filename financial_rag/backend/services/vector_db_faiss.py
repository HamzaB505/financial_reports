import os
import shutil
import argparse
from tqdm import tqdm

from langchain.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .embedder import Embedder  # Make sure to import your Embedder class

from dotenv import load_dotenv
import logging
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class VectorDBFaiss:
    """
    VectorDB class for managing document embeddings and vector database operations.

    This class provides methods to:
    - Initialize the vector database
    - Add documents to the FAISS vector store
    - Split documents into smaller chunks
    - Create unique IDs for document chunks

    It uses an Embedder for document embedding and FAISS as the vector store.
    """
    def __init__(self, embedder):
        self.embedder = embedder
        self.vector_db = None

    def add_to_faiss(self, chunks: list[Document], faiss_index_path: str):
        logger.info('Starting embedding')

        # Embed the chunks
        embeddings = self.embedder.embed_documents([chunk.page_content for chunk in chunks])

        logger.info("Finished embedding")
        chunks_with_ids = self.create_chunk_ids(chunks)

        if os.path.exists(faiss_index_path):
            # Load existing FAISS index
            index = FAISS.load_local(faiss_index_path)
        else:
            # Create a new FAISS index
            dimension = len(embeddings[0])
            index = FAISS(FAISS.build_index(np.array(embeddings), dimension=dimension), chunk_size=512)

        # Add new chunks to the index
        new_chunk_ids = [chunk.metadata["id"] for chunk in chunks_with_ids]
        index.add_texts(texts=[chunk.page_content for chunk in chunks_with_ids], ids=new_chunk_ids, embeddings=embeddings)

        # Save the index
        index.save_local(faiss_index_path)
        logger.info(f"Saved {len(chunks_with_ids)} chunks to {faiss_index_path}")

        self.vector_db = index

    def split_documents(self, documents: list[Document]):
        """
        Split documents into smaller chunks.

        This method takes a list of documents and splits them into smaller chunks
        using a RecursiveCharacterTextSplitter. It's useful for preparing documents
        for embedding and storage in a vector database.

        Args:
            documents (list[Document]): A list of documents to be split.

        Returns:
            list[Document]: A list of document chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=500,
            length_function=len,
            add_start_index=True,
            is_separator_regex=False,
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        
        return chunks

    def create_chunk_ids(self, chunks):
        """
        Create unique IDs for document chunks.

        This static method generates a unique ID for each chunk based on its source,
        page number, and position within the page. It modifies the chunks in-place
        by adding an 'id' field to each chunk's metadata.

        Parameters:
            chunks (list[Document]): A list of document chunks to process.

        Returns:
            list[Document]: The input list of chunks with added 'id' metadata.
        """
        last_page_id = None
        current_chunk_index = 0

        logger.info("Creating chunks")

        for chunk in tqdm(chunks):
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            # if the page ID is the same as the last one, increment the index
            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0
            # Calculate the chunk ID.
            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            chunk.metadata["id"] = chunk_id
        logger.info("Chunks created")

        return chunks

    def clear_database(self, faiss_index_path):
        if os.path.exists(faiss_index_path):
            os.remove(faiss_index_path)

    def save_to_faiss(self, chunks: list[Document], faiss_index_path: str):
        """
        Save document chunks to a FAISS vector database.

        Args:
            chunks (list[Document]): A list of document chunks to be saved.
            faiss_index_path (str): The file path where the FAISS index will be persisted.

        This method creates a new FAISS vector database from the provided document chunks,
        using the embedder defined in the class instance. The database is then persisted
        to the specified file path.

        Note:
            - The `chunks` should be pre-processed and contain necessary metadata.
            - This method uses the embedding function from the class instance.
        """
        # Embed the chunks
        embeddings = self.embedder.embed_documents([chunk.page_content for chunk in chunks])

        # Create a new FAISS index
        dimension = len(embeddings[0])
        index = FAISS(FAISS.build_index(np.array(embeddings), dimension=dimension), chunk_size=512)
        
        # Add chunks to the index
        new_chunk_ids = [chunk.metadata["id"] for chunk in chunks]
        index.add_texts(texts=[chunk.page_content for chunk in chunks], ids=new_chunk_ids, embeddings=embeddings)
        
        # Save the index
        index.save_local(faiss_index_path)
        logger.info(f'Saved {len(chunks)} chunks to {faiss_index_path}')

        self.vector_db = index
