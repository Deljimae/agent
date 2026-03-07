import json
from config import client, MAX_MESSAGES
from tools.registry import tools, AVAILABLE_TOOLS
from agent.logger import log_step, print_conversation
from agent.memory import save_memory_notes



SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a versatile research assistant with access to real-time tools.\n\n"
        "1. EXA SEARCH: Use this for web-based queries. Cite source URLs.\n"
        "2. WEATHER DATA: Use this for current conditions using coordinates.\n\n"
        "Choose the most appropriate tool. You may use multiple in sequence."
    ),
}


def execute_tool_calls(tool_call):
    f_name = tool_call.name
    f_args = json.loads(tool_call.arguments)
    function_to_call = AVAILABLE_TOOLS.get(f_name)

    if function_to_call:
        results = function_to_call(**f_args)
        return {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(results)
        }
    raise ValueError(f"Unknown tool: {f_name}")




def run_agent(user_query, conversation):

    conversation.append({"role": "user", "content": user_query})

    # SLIDING WINDOW LOGIC
    while len(conversation) > MAX_MESSAGES:
        if len(conversation) > 1:
            conversation.pop(1)
        

    iteration_count = 0
    total_tools_executed = 0

    while True:
        iteration_count += 1
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=tools,
            input=conversation,
        )

        # Append model output to conversation
        conversation += response.output

        # Collect tool calls
        tool_calls = [
            item for item in response.output 
            if item.type == "function_call"
        ]

        # NEW: Print the formatted log for this turn
        log_step(iteration_count, tool_calls)
        total_tools_executed += len(tool_calls)
        

        if not tool_calls:
            # Print Final Summary before breaking
            print(f"\n{'*'*10} AGENT FINISHED {'*'*10}")
            print(f"Total Iterations: {iteration_count}")
            print(f"Total Tool Calls: {total_tools_executed}")
            print(f"{'*'*36}\n")
            print(response.output_text)
            print_conversation(conversation)
            print(conversation)
            break

        # Execute each tool call
        for tool_call in tool_calls:
            tool_result = execute_tool_calls(tool_call)
            conversation.append(tool_result)


