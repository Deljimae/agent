import asyncio
from agent.core import run_agent, SYSTEM_MESSAGE
from agent.memory import load_long_term_memory, save_memory_notes
from agent.reflection import reflect_on_session
from agent.mcp_client import LocalMCPClient # The bridge you wrote

async def main():
    print("--- AI Agent + Local-Intel MCP Active ---")
    
    # 1. Start the MCP Bridge
    mcp_bridge = LocalMCPClient()
    await mcp_bridge.connect()
    
    session_history = [SYSTEM_MESSAGE]
    
    try:
        while True:
            user_query = input("\nQuery (or 'exit'): ")
            if user_query.lower() in ["exit", "quit"]:
                print("Reflecting... 🧠")
                reflections = reflect_on_session(session_history)
                save_memory_notes(reflections)
                break
            
            if not user_query.strip(): continue

            session_history.append({"role": "user", "content": user_query})

            # Memory Retrieval
            relevant_memories = load_long_term_memory(user_query)
            memory_context = {"role": "system", "content": f"PREVIOUS KNOWLEDGE:\n{relevant_memories}"}
            
            # Note: We don't append memory_context to session_history to avoid bloat
            turn_history = [memory_context] + session_history
            
            # 2. Run the Async Agent
            response_object = await run_agent(user_query, turn_history, mcp_client=mcp_bridge)

            # Persist short-term
           
            session_history.append({"role": "assistant", "content": response_object.output_text})

    finally:
        # 3. Always close the connection
        await mcp_bridge.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
