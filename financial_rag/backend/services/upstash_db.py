from dotenv import load_dotenv
import os
from upstash_vector import Index


load_dotenv()


index = Index(url=os.environ["UPSTASH_API_URL"],
              token=os.environ["UPSTASH_API_KEY"])



