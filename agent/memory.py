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


def search_semantic_memory(query_text, top_k=5):
    """
    1. Turns the user query into a vector.
    2. Compares it against ALL stored facts.
    3. Returns the top 5 most relevant facts.
    """
    query_vector = get_embedding(query_text)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fact, category, vector FROM semantic_memory")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    results = []
    for fact, category, blob in rows:
        stored_vector = pickle.loads(blob) # Unpickle the vector
        score = cosine_similarity(query_vector, stored_vector)
        results.append((score, fact, category))

    # Sort by highest similarity score
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

# --- STAGE 3: THE RETRIEVAL (Load Logic) ---
def load_long_term_memory(user_query):
    """
    The 'Search Engine'. Finds the most relevant bits of 
    info based on what the user just said.
    """
    # Use our semantic search function from Stage 3
    results = search_semantic_memory(user_query, top_k=5)
    
    if not results:
        return "No relevant past memories found."

    context = "\nRELEVANT MEMORIES:\n"
    for score, fact, cat in results:
        context += f"- [{cat}] {fact} (Match: {score:.2f})\n"
    
    return context