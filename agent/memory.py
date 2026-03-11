import sqlite3
import pickle
import numpy as np
from datetime import datetime
from agent.embeddings import get_embedding

DB_FILE = "agent_brain.db"

def init_db():
    """Initializes the 3-tier memory system."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. SEMANTIC TABLE (Facts/Knowledge)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS semantic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT UNIQUE,
            category TEXT,
            vector BLOB,
            timestamp DATETIME
        )
    ''')

    # 2. EPISODIC TABLE (Events/History)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            outcome TEXT,
            vector BLOB,
            timestamp DATETIME
        )
    ''')

    # 3. PROCEDURAL TABLE (Rules/Skills)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procedural_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule TEXT,
            context TEXT,
            vector BLOB,
            timestamp DATETIME
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# --- HELPER: VECTOR MATH ---
def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def search_memory_tier(table_name, query_vector, top_k=3, threshold=0.70):
    """Generic search for any of the 3 memory tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Dynamically select columns based on table
    columns = "*" 
    cursor.execute(f"SELECT {columns} FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        # Tables have different structures, but vector is always the 2nd to last col
        stored_vector = pickle.loads(row[-2]) 
        score = cosine_similarity(query_vector, stored_vector)
        
       
        results.append((score, row))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]

# --- STAGE 2: THE VAULT (Save Logic) ---
def save_memory_notes(reflection_json):
    """
    Takes the structured JSON from the Reflection Engine and 
    saves it into the 3-tier system with embeddings.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    # 1. Save Semantic Facts
    for item in reflection_json.get("semantic", []):
        vector = get_embedding(item["fact"])
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_memory (fact, category, vector, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (item["fact"], item["category"], pickle.dumps(vector), now))

    # 2. Save Episodes (Events)
    for item in reflection_json.get("episodic", []):
        vector = get_embedding(item["event"])
        cursor.execute('''
            INSERT INTO episodic_memory (event, outcome, vector, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (item["event"], item["outcome"], pickle.dumps(vector), now))

    # 3. Save Procedures (Rules)
    for item in reflection_json.get("procedural", []):
        vector = get_embedding(item["rule"])
        cursor.execute('''
            INSERT INTO procedural_memory (rule, context, vector, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (item["rule"], item["context"], pickle.dumps(vector), now))

    conn.commit()
    conn.close()


def load_long_term_memory(user_query):
    """
    The 'Tri-Core' Search: Finds relevant Facts, Rules, and Past Experiences.
    """
    query_vector = get_embedding(user_query)
    
    # 1. Search all tiers
    semantic_hits = search_memory_tier("semantic_memory", query_vector)
    episodic_hits = search_memory_tier("episodic_memory", query_vector)
    procedural_hits = search_memory_tier("procedural_memory", query_vector)

    if not (semantic_hits or episodic_hits or procedural_hits):
        return "No relevant past memories found."

    context = "\n=== LONG-TERM MEMORY RETRIEVED ===\n"

    if semantic_hits:
        context += "\n[KNOWLEDGE & FACTS]:\n"
        for score, row in semantic_hits:
            context += f"- {row[1]} (Category: {row[2]})\n"

    if procedural_hits:
        context += "\n[RULES & PROCEDURES]:\n"
        for score, row in procedural_hits:
            context += f"- RULE: {row[1]} | CONTEXT: {row[2]}\n"

    if episodic_hits:
        context += "\n[PAST EXPERIENCES]:\n"
        for score, row in episodic_hits:
            context += f"- EVENT: {row[1]} | OUTCOME: {row[2]}\n"
    
    return context + "\n==================================\n"
