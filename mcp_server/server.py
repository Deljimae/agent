import os
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("Local-Intel")

# Root detection logic
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if "mcp_server" in ROOT_DIR:
    ROOT_DIR = os.path.dirname(ROOT_DIR)

@mcp.tool()
def inspect_project() -> str:
    """Lists only clean, relevant project files (ignores hidden/cache)."""
    files_found = []
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
        for file in files:
            if file.startswith(('.', '__')): continue
            rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
            files_found.append(rel_path)
    return "\n".join(files_found) if files_found else "No relevant files found."

@mcp.tool()
def read_code_file(file_path: str) -> str:
    """Reads the content of a specific code file from the project."""
    full_path = os.path.join(ROOT_DIR, file_path)
    if not os.path.exists(full_path):
        return f"Error: File '{file_path}' not found."
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"--- CONTENT OF {file_path} ---\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_research_log(filename: str, content: str) -> str:
    """
    Writes or appends research notes to a local file.
    Use this to save search results for the user to read later.
    """
    # 1. Safety: Force file extension to be .md or .txt
    if not (filename.endswith(".md") or filename.endswith(".txt")):
        filename += ".md"
        
    full_path = os.path.join(ROOT_DIR, filename)
    
    try:
        # 2. Append mode ('a') ensures we don't delete previous notes
        with open(full_path, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            f.write(f"\n\n--- AGENT LOG: {timestamp} ---\n")
            f.write(content)
            f.write("\n" + "="*30 + "\n")
        return f"Successfully saved research to '{filename}' at {ROOT_DIR}."
    except Exception as e:
        return f"Error writing file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
