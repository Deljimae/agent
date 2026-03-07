from datetime import datetime, timedelta
from config import exa

def exa_search(query: str):
    # 1. Fetch minimal results
    response = exa.search(
        query=query, 
        type='auto', 
        num_results=2,  # Drop to 2 results for maximum savings
        start_published_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        contents={"text": {"max_characters": 300}} # Drop to 300 chars
    )
    
    # 2. MANUALLY extract only what the LLM needs
    # This turns a massive object into a tiny, clean list of dicts
    cleaned_results = []
    for r in response.results:
        cleaned_results.append({
            "title": r.title,
            "url": r.url,
            "content": r.text  # Only the text snippet
        })
        
    return cleaned_results