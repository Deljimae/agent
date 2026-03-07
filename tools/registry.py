from tools.weather import get_weather
from tools.search import exa_search

AVAILABLE_TOOLS = {
    "exa_search": exa_search,
    "get_weather": get_weather,
}

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather conditions and daily forecast for a specific location using latitude and longitude coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number", 
                    "minimum": -90, 
                    "maximum": 90,
                    "description": "The precise latitude of the location (e.g., 6.4550 for Lagos, Nigeria)."
                },
                "lon": {
                    "type": "number", 
                    "minimum": -180, 
                    "maximum": 180,
                    "description": "The precise longitude of the location (e.g., 3.3841 for Lagos, Nigeria)."
                },
            },
            "required": ["lat", "lon"],
            "additionalProperties": False
        },
    },
    {
        "type": "function",
        "name": "exa_search",
        "description": "Perform a search query on the web, and retrieve the most relevant URLs/web data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search keywords or natural language question to look up on the web (e.g., 'current CEO of Apple' or 'Tokyo coordinates')."
                },
            },
            "required": ["query"],
        },
    },
]
