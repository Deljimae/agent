import requests
from config import OPENWEATHER_API_KEY


def get_weather(lat, lon):
    """
    Fetches weather data and returns a cleaned dictionary 
    optimized for an LLM Agent's context.
    """
    # Use 'exclude' to save bandwidth and keep the response small
    exclude = "minutely,hourly"
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 2. Focus on Semantic Fields
        # We extract only what an agent needs to hold a conversation
        current = data.get("current", {})
        daily_today = data.get("daily", [{}])[0]

        weather_summary = {
            "location_coords": {"lat": lat, "lon": lon},
            "current_condition": current.get("weather", [{}])[0].get("description"),
            "temperature": {
                "actual": f"{current.get('temp')}°C",
                "feels_like": f"{current.get('feels_like')}°C"
            },
            "humidity": f"{current.get('humidity')}%",
            "uv_index": current.get("uvi"),
            "today_forecast": {
                "summary": daily_today.get("summary"), # One Call 3.0 specific human-readable string
                "pop_chance": f"{int(daily_today.get('pop', 0) * 100)}%", # Prob. of precipitation
                "temp_range": f"{daily_today.get('temp', {}).get('min')}°C to {daily_today.get('temp', {}).get('max')}°C"
            },
            "alerts": data.get("alerts", "No active weather alerts")
        }

        return weather_summary

    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}

# --- Experimenting with Lagos ---
#OMU_ARAN_LAT = 8.1386
#OMU_ARAN_LON = 5.1026

#weather_data = get_weather(OMU_ARAN_LAT, OMU_ARAN_LON)
#print(weather_data)
