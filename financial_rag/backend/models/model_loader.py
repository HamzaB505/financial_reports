from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMModels:

    def __init__(self):
        self.openai_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        self.parser = StrOutputParser()
        self.history= []

    def add_context(self, prompt):
        """Add a new prompt to the context."""
        self.history.append({"role": "user", "content": prompt})

    def query_model(self, prompt):
        """Query the model using the chain invocation pattern."""
        self.add_context(prompt)
        # Construct the chain: messages -> model -> parser
        chain = self.openai_model | self.parser

        # Invoke the chain to get the response
        response = chain.invoke({"input": prompt})
        return response

