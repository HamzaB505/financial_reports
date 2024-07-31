from transformers import AutoModel, AutoTokenizer
import openai
from openai import OpenAI
import torch
from tqdm import tqdm

class ModelLoader:
    """
    This method explains the functionality of the ModelLoader class.

    The ModelLoader class is responsible for loading and managing models for embedding text and querying OpenAI's API.

    Key components:
    1. Initialization (__init__):
       - Stores the configuration, including the OpenAI API key.
       - Initializes embedding_model and tokenizer as None.

    2. load_embedding_model:
       - Loads a pre-trained model and tokenizer based on the configuration.
       - Uses the Hugging Face Transformers library.

    3. get_embeddings:
       - Converts input text into embeddings using the loaded model.
       - Tokenizes the input, passes it through the model, and returns the mean of the last hidden state.

    4. query_openai:
       - Sends a prompt to OpenAI's API for text completion.
       - Uses the stored API key for authentication.
       - Returns the generated text response.

    This class combines local embedding capabilities with OpenAI's powerful language model,
    allowing for versatile text processing and generation tasks.
    """
    def __init__(self, **config):
        self.config = config
        self.embedding_model = None
        self.tokenizer = None
        self.openai_api_key = config['openai_api_key']
        self.client = OpenAI()

    def load_embedding_model(self):
        model_name = self.config['embedding_model']
        self.embedding_model = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def get_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def query_openai(self, prompt):
        openai.api_key = self.openai_api_key

        # gets API Key from environment variable OPENAI_API_KEY
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt
            )
        output = completion.choices[0].message.content

        return output