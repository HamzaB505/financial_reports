from upstash_vector import Index
from dotenv import load_dotenv
from langchain_community.vectorstores.upstash import UpstashVectorStore
from load_documents import load_documents
import os
from llama_index.embeddings.openai import OpenAIEmbedding
import logging
from upstash_vector import Vector
from tqdm.auto import tqdm

logging.basicConfig(level=logging.INFO)

load_dotenv()
def enrich_metadata(document):
    doc_name = document.metadata["source"].split("/")[-1].split(".")[0]
    if "qtr" in doc_name:
        document.metadata["year"] = f"""20{doc_name.split("qtr")[-1]}"""
        document.metadata["quarter"] = doc_name.split("qtr")[0]
    elif "ar" in doc_name:
        document.metadata["year"] = doc_name.split("ar")[0]
        document.metadata["quarter"] = ""
    document.metadata["data"] = document.page_content


openai_embedding_model = "text-embedding-3-small"
embedder = OpenAIEmbedding(model=openai_embedding_model)

logging.info("model loaded")


documents = load_documents(DATA_PATH="../../../data/documents/Finance/Berkshire Hathaway")

vector_store = []
for i, doc in tqdm(enumerate(documents[:10])):
    if doc.page_content:
        embeddings = embedder.get_text_embedding(doc.page_content)
        enrich_metadata(document=doc)
        v = Vector(id=f"id_{i}", vector=embeddings, metadata=doc.metadata, data=doc.page_content)
        vector_store.append(v)
print(vector_store)
logging.info("Documents loaded & embedded")


index = Index(url=os.environ["UPSTASH_VECTOR_REST_URL_Berkshire"],
              token=os.environ["UPSTASH_VECTOR_REST_TOKEN_Berkshire"]
              )
logging.info("index initiated")

index.upsert(
    vectors=vector_store,
    namespace="Berkshire_Hathaway"
)
logging.info("vectorstore loaded with info")
