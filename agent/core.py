import json
import asyncio
from config import client, MAX_MESSAGES
from tools.registry import tools as static_tools, AVAILABLE_TOOLS
from agent.logger import log_step, print_conversation

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a versatile research assistant with access to real-time tools.\n\n"

        "Available tools:\n"
        "1. EXA SEARCH – Use this for web-based queries. Always cite source URLs.\n"
        "2. WEATHER DATA – Use this to retrieve current weather conditions using coordinates.\n\n"

        "Instructions:\n"
        "- Choose the most appropriate tool for the task.\n"
        "- You may use multiple tools in sequence if necessary."
    ),
}


async def run_agent(user_query, conversation, mcp_client=None):
    # 1. Merge static tools with MCP tools
    all_tools = list(static_tools)
    mcp_tool_definitions = []
    
    if mcp_client:
        # Get dynamic tools from your local server
        raw_mcp = await mcp_client.session.list_tools()
        mcp_tool_definitions = mcp_client.translate_to_openai(raw_mcp.tools)
        all_tools.extend(mcp_tool_definitions)

    # Sliding window logic
    while len(conversation) > MAX_MESSAGES:
        if len(conversation) > 1: conversation.pop(1)

    iteration_count = 0
    total_tools_executed = 0

    while True:
        iteration_count += 1
        # Use the Async OpenAI call
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=all_tools,
            input=conversation,
        )

        conversation += response.output
        tool_calls = [item for item in response.output if item.type == "function_call"]
        
        log_step(iteration_count, tool_calls)
        total_tools_executed += len(tool_calls)

        if not tool_calls:
            print(f"\n{'*'*10} AGENT FINISHED {'*'*10}")
            print(response.output_text)
            break

        for tool_call in tool_calls:
            f_name = tool_call.name
            f_args = json.loads(tool_call.arguments)

            # BRANCH: Is it a Static Tool or an MCP Tool?
            if f_name in AVAILABLE_TOOLS:
                # Handle static tools (Weather/Exa) - these are sync
                result = AVAILABLE_TOOLS[f_name](**f_args)
            else:
                # Handle MCP tools (File Intel) - these are async
                print(f"  [MCP] Routing to Local Server: {f_name}")
                result = await mcp_client.call_tool(f_name, f_args)

            conversation.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result)
            })

    return response
