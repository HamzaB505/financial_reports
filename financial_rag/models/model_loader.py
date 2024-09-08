from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

class LLMModels:

    def __init__(self):
        self.openai_model = OpenAI()
        self.parser = StrOutputParser()
        self.history= []

    def save_to_history(self, prompt):
        """Add a new prompt to the context."""
        self.history.append({"role": "user", "content": prompt})

    def query_model(self, messages):
        print('inside query function')
        print(self.openai_model)
        completion = self.openai_model.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
            )
        print("completion end")
        response = completion.choices[0].message.content

        print(response)
        print("response end")
        return response
