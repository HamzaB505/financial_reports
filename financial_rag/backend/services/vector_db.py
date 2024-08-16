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

        logger.info("Crearting chunks")

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

    def clear_database(self, CHROMA_PATH):
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)

    def save_to_chroma(self,
                       chunks: list[Document],
                       chroma_path: str):

        """
        Save document chunks to a Chroma vector database.

        Args:
            chunks (list[Document]): A list of document chunks to be saved.
            chroma_path (str): The directory path where the Chroma database will be persisted.

        This method creates a new Chroma vector database from the provided document chunks,
        using the embedder defined in the class instance. The database is then persisted
        to the specified directory.

        Note:
            - The `chunks` should be pre-processed and contain necessary metadata.
            - The `chroma_path` directory will be created if it doesn't exist.
            - This method uses the embedding function from the class instance.
        """
        # create a new embeddings DB from the documents
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding_function=self.embedder,
            persist_directory=chroma_path
        )
        vector_db.persist()
        logger.info(f'Saved {len(chunks)} chunks to {chroma_path}')

