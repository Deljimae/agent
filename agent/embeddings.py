import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    """
    Turns a string into a list of 1,536 numbers (a Vector).
    'text-embedding-3-small' is cheap, fast, and very accurate.
    """
    # Clean the text (remove newlines which can mess up embeddings)
    text = text.replace("\n", " ")
    
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    
    # Return the list of floats (the actual vector)
    return response.data[0].embedding

# Quick test if run directly
# if __name__ == "__main__":
#    test_text = "I love building AI agents"
#    vector = get_embedding(test_text)
#   print(f"Vector length: {len(vector)}")
#    print(f"First 5 numbers: {vector[:5]}")
