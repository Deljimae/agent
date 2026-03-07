import json

def log_step(step, tool_calls):
    print(f"\n{'='*15} ITERATION {step} {'='*15}")
    print(f"Tool Calls this turn: {len(tool_calls)}")
    for i, tool in enumerate(tool_calls, 1):
        print(f"  [{i}] Executing: {tool.name}")
        print(f"      Arguments: {tool.arguments}")
        

def print_conversation(conversation):
    print("\n" + "="*20 + " CONVERSATION HISTORY " + "="*20)
    for msg in conversation:
        # --- Case 1: Standard Dictionaries (User/System/Tool Results) ---
        if isinstance(msg, dict):
            # Safe way to get role without crashing
            role = msg.get("role", msg.get("type", "TOOL")).upper()
            
            # Print text content (User/System)
            if "content" in msg and isinstance(msg["content"], str):
                print(f"\n[{role}]: {msg['content']}")
            
            # Print Tool Results (formatted JSON)
            elif msg.get("type") == "function_call_output":
                print(f"\n[TOOL RESULT - ID: {msg.get('call_id', 'unknown')[:8]}...]:")
                try:
                    data = json.loads(msg["output"])
                    print(json.dumps(data, indent=4))
                except:
                    print(msg["output"])

        # --- Case 2: SDK Objects (Assistant/Tool Calls) ---
        else:
            # Handle the ResponseFunctionToolCall objects
            if hasattr(msg, 'type') and msg.type == "function_call":
                print(f"\n[ASSISTANT CALLING TOOL]: {msg.name}")
                print(f"Arguments: {msg.arguments}")
            
            # Handle the final Text Response objects
            elif hasattr(msg, 'type') and msg.type == "message":
                # Assuming response.output_text was used in your logic
                # We pull the actual text from the content list if needed
                print(f"\n[ASSISTANT]: (Final Response Provided)")

    print("\n" + "="*20 + " END OF HISTORY " + "="*20 + "\n")
