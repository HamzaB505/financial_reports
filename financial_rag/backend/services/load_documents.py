import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from PyPDF2.errors import PdfStreamError
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from upstash_vector import Vector
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



def prepare_source(documents):
    for doc in tqdm(documents):
        source_data_split = doc.metadata["source"].split("\\")

        source_data_split = list(dict.fromkeys(source_data_split))
        k = [source_data_split.remove(l) for l in ["..", "data", "documents"] if l in source_data_split]
            
        source = '/'.join([str(elem) for elem in source_data_split])
        doc.metadata["source"] = source

def split_documents(documents: list[Document]):
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

def semantic_split(documents):
    text_splitter = SemanticChunker(OpenAIEmbeddings())
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")

    return chunks

def load_documents(DATA_PATH):
    documents = []
    
    def process_directory(dir_path):
        nonlocal documents
        
        items = os.listdir(dir_path)
        subdirs = [d for d in items if os.path.isdir(os.path.join(dir_path, d))]
        pdf_files = [f for f in items if f.lower().endswith('.pdf')]
        txt_files = [f for f in items if f.lower().endswith('.txt')]
        
        if not items or (not pdf_files and not txt_files and not subdirs):
            logging.info(f"No relevant files or subdirectories in {dir_path}, skipping...")
            return
        
        if pdf_files:
            logging.info(f"PDF files found in {dir_path}: {pdf_files}")
            document_loader = PyPDFDirectoryLoader(dir_path)
            try:
                # Try to load the documents and append to the documents list
                loaded_docs = document_loader.load()
                documents.extend(loaded_docs)
                logging.info(f"Successfully loaded {len(loaded_docs)} documents from PDFs in {dir_path}.")
            except PdfStreamError as e:
                logging.error(f"Error loading PDF in {dir_path}: {str(e)} - File might be corrupted.")
            except Exception as e:
                # Catch any other exceptions that may occur during PDF loading
                logging.error(f"Unexpected error loading PDFs in {dir_path}: {str(e)}")

        for txt_file in txt_files:
            try:
                loader = TextLoader(os.path.join(dir_path, txt_file))
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logging.info(f"Successfully loaded {len(loaded_docs)} documents from TXT file {txt_file}.")
            except Exception as e:
                logging.error(f"Error loading TXT file {txt_file} in {dir_path}: {str(e)}")

        for subdir in subdirs:
            process_directory(os.path.join(dir_path, subdir))
    
    process_directory(DATA_PATH)
    logging.info(f"Total documents loaded: {len(documents)}")
    prepare_source(documents)
    logging.info(f"Formatted source correctly")

    return documents


def create_chunk_ids(chunks):
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

def enrich_metadata(document):
    doc_name = document.metadata["source"].split("/")[-1].split(".")[0]
    if "qtr" in doc_name:
        document.metadata["year"] = f"""20{doc_name.split("qtr")[-1]}"""
        document.metadata["quarter"] = doc_name.split("qtr")[0]
    elif "ar" in doc_name:
        document.metadata["year"] = doc_name.split("ar")[0]
        document.metadata["quarter"] = ""

def create_vectorstore(documents, embedder):
    vector_store = []
    for i, doc in tqdm(enumerate(documents)):
        if doc.page_content:
            embeddings = embedder.get_text_embedding(doc.page_content)
            enrich_metadata(doc)
            v = Vector(id=f"id_{i}", vector=embeddings,
                       metadata=doc.metadata, data=doc.page_content)
            vector_store.append(v)
    logging.info("Documents loaded & embedded")
    return vector_store