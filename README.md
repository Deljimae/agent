## 🚀 Getting Started

### Prerequisites
- [uv](https://docs.astral.sh) installed (Fast Python package manager).
- OpenAI, Exa, and OpenWeather API Keys.

### Installation
1. **Clone the repository**:
   ```bash
   git clone <https://github.com/Deljimae/agent>
   cd AGENTS

2. **env variables**:

    OPENAI_API_KEY=your_key_here

    EXA_API_KEY=your_key_here

    OPENWEATHER_API_KEY=your_key_here

3. **Run the Agent**
    ```bash
    uv run main.py


## 🎯 Example Queries to Try

Once the agent is running, try these "stress tests" to see the MCP and Memory systems in action:

1. **The Directory Check (MCP Discovery)**:
   > "List the files in my project to make sure you can see them."
   *Tests: `inspect_project` tool and local server connectivity.*

2. **The Self-Awareness Test (Local Intelligence)**:
   > "Read the code in agent/mcp_client.py and explain how you connect to the local server."
   *Tests: `read_code_file` and the agent's ability to analyze its own architecture.*

3. **The Multi-Tool Research (Full Orchestration)**:
   > "Search Exa for the latest news on MCP servers, then save a summary of what you find to a new file called mcp_research.md."
   *Tests: Cloud Search (Exa) + Reasoning + Local Write (MCP `write_research_log`) in one autonomous loop.*
