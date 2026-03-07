from agent.core import run_agent, SYSTEM_MESSAGE
from agent.memory import load_long_term_memory, save_memory_notes
from agent.reflection import reflect_on_session # Import the new engine

def main():
    print("--- AI Research Agent (with 3-Tier Vector LTM) Active ---")
    
    # Initialize session history
    session_history = [SYSTEM_MESSAGE]
    
    # 1. BOOTSTRAP: Get a small greeting/query to prime the Vector Search
    initial_greet = "Hello! I am ready to help."
    
    while True:
        try:
            user_query = input("\nWhat do you want to search for? (type 'exit' to stop): ")
            
            if user_query.lower() in ["exit", "quit"]:
                # 3. SAVE: Before quitting, run the 3-tier Reflection
                print("Reflecting on our conversation... 🧠")
                reflections = reflect_on_session(session_history)
                save_memory_notes(reflections) # This handles the SQLite + Vectors
                print("Memories secured. Goodbye!")
                break
                
            if not user_query.strip():
                continue

            session_history.append({"role": "user", "content": user_query})


            # 2. DYNAMIC LOAD: Pull only the 5 most relevant memories for THIS specific query
            relevant_memories = load_long_term_memory(user_query)
            # Inject memories into a fresh temporary System Message for this turn
            memory_context = {"role": "system", "content": f"PREVIOUS KNOWLEDGE:\n{relevant_memories}"}

            turn_history = [memory_context] + session_history
                
            # Pass history to agent
            response_object = run_agent(user_query, turn_history)

            assistant_text = response_object.output_text

            # 5. PERSIST: Add the Assistant's response to Short-Term Memory
            session_history.append({"role": "assistant", "content": assistant_text})
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
