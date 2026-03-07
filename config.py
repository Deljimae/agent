import os
from dotenv import load_dotenv
from openai import OpenAI
from exa_py import Exa

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Initialize clients once
client = OpenAI()
exa = Exa(api_key=EXA_API_KEY)

MAX_MESSAGES = 10 
