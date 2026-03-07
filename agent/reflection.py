import os
import json
from agent.core import client


REFLECTION_PROMPT = """
You are a 'Memory Secretary' for an AI Agent. Your job is to analyze the conversation history and extract 3 types of long-term memories.

1. SEMANTIC (Facts): Permanent info about the user (name, location, preferences, job).
2. EPISODIC (Events): Notable successes or failures. What happened? Did a tool work or fail? 
3. PROCEDURAL (Rules): Best practices or workflows. How should the agent behave next time? (e.g., 'Always use Celsius for this user').

Output ONLY a valid JSON object with this structure:
{
  "semantic": [{"fact": "...", "category": "..."}],
  "episodic": [{"event": "...", "outcome": "..."}],
  "procedural": [{"rule": "...", "context": "..."}]
}

If no new information is found for a category, return an empty list for it.
"""


def reflect_on_session(chat_history):
    # ... existing prompt and setup ...

    response = client.responses.create(
        model="gpt-4o-mini",
        input=chat_history + [{"role": "user", "content": REFLECTION_PROMPT}]
    )

    try:
        # Use the dedicated helper for the new Responses API
        raw_text = response.output_text.strip() 
        
        # Standard cleaning in case the model wraps JSON in markdown blocks
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(raw_text)
    except Exception as e:
        print(f"Reflection Parsing Error: {e}")
        # Return empty structure so save_memory_notes doesn't crash
        return {"semantic": [], "episodic": [], "procedural": []}



