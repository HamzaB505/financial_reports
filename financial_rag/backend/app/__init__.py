from dotenv import load_dotenv
import os
import logging
import sys


load_dotenv()  # Load environment variables from .env file

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

logger = logging.getLogger("RAG")
logger.setLevel(logging.INFO)
logger.propagate = True
if not logger.handlers:
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.INFO)
    logger.addHandler(consolehandler)
    formatter = logging.Formatter('%(name)s :: %(levelname)s :: %(message)s')
    consolehandler.setFormatter(formatter)
    
