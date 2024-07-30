from models.model_loader import ModelLoader

class Embedder:
    """
    The Embedder class is responsible for embedding documents using a pre-trained model.

    Key components:
    1. Initialization (__init__):
       - Creates a ModelLoader instance with the provided configuration.
       - Loads the embedding model using the ModelLoader.

    2. embed_documents method:
       - Takes a list of documents as input.
       - Iterates through each document, generating an embedding using the loaded model.
       - Returns a list of embeddings corresponding to the input documents.

    This class serves as a wrapper around the ModelLoader, providing a simple interface
    for embedding multiple documents. It's designed to work with the financial BERT model
    specified in the configuration, making it suitable for processing financial texts.
    """
    def __init__(self, config):
        self.model_loader = ModelLoader(config)
        self.model_loader.load_embedding_model()

    def embed_documents(self, documents):
        embeddings = []
        for doc in documents:
            embedding = self.model_loader.get_embeddings(doc)
            embeddings.append(embedding)
        return embeddings
