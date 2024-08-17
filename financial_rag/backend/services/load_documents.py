import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from PyPDF2.errors import PdfStreamError
from tqdm import tqdm




def prepare_source(documents):
    for doc in tqdm(documents):
        source_data_split = doc.metadata["source"].split("\\")

        source_data_split = list(dict.fromkeys(source_data_split))
        k = [source_data_split.remove(l) for l in ["..", "data", "documents"]]
            
        source = '/'.join([str(elem) for elem in source_data_split])
        doc.metadata["source"] = source


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
