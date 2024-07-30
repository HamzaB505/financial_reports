from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
import os
import logging

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)


def load_documents(DATA_PATH):
    files = os.listdir(DATA_PATH)
    logger.info(f"Files found: {files}")
    file_texts = []
    documents = []
    txt_files = [file for file in files if "txt" in file]
    if "pdf" in files[0]:
      document_loader = PyPDFDirectoryLoader(DATA_PATH)
      documents = document_loader.load()
    else:
      for file in txt_files:
        loader = TextLoader(f"{DATA_PATH}/{file}")
        file_texts.append(loader.load()[0])
    documents = documents + file_texts
    logger.info(len(documents))
    return documents
