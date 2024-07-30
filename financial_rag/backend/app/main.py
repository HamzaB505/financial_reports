import yaml
from scraper.scraper import Scraper
from processor.embedder import Embedder
from database.vector_db import VectorDB
from api.query_handler import QueryHandler

def main():
    """
    This function serves as the main entry point for the financial report analysis system.
    It performs the following steps:
    1. Loads the configuration from a YAML file.
    2. Initializes key components: Scraper, Embedder, VectorDB, and QueryHandler.
    3. Scrapes financial reports using the Scraper.
    4. Embeds the scraped documents using the Embedder.
    5. Adds the embeddings to the VectorDB.
    6. Processes a sample query using the QueryHandler.

    The function demonstrates the end-to-end flow of the system, from data collection
    to query processing, showcasing how different components interact to provide
    insights from financial reports.
    """
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    scraper = Scraper(config)
    embedder = Embedder(config)
    vector_db = VectorDB(config['embedding_dimension'])
    query_handler = QueryHandler(config, vector_db)

    # Scraping
    documents = scraper.scrape_financial_reports()

    # Embedding
    embeddings = embedder.embed_documents(documents)

    # Updating Vector DB
    vector_db.add_vectors(embeddings)

    # Example query
    result = query_handler.process_query("What were the top performing sectors last quarter?")
    print(result)

if __name__ == "__main__":
    main()