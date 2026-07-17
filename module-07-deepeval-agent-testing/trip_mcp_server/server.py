# server.py
# A local, standalone MCP server for trip planning — the "tools" side of the
# module 7 MCP demo. Built with the official `mcp` SDK's FastMCP helper, it
# runs over stdio (the transport an MCP client launches as a subprocess), and
# exposes three tools that the trip_agent chains together per query:
#
#   geocode(place)                              -> {name, country, latitude, longitude}
#   get_weather(latitude, longitude, days)      -> {current, forecast[]}
#   suggest_packing(temp_max_c, temp_min_c,     -> {summary, items[]}
#                   conditions)
#
# geocode + get_weather hit the free open-meteo.com API (no key). suggest_packing
# is pure logic. The intended chain for "what should I pack for <place>?" is
# geocode -> get_weather -> suggest_packing, which is exactly the multi-step tool
# usage the DeepEval metrics in ci/ (and LangSmith tracing in trip_agent) are
# there to inspect.
#
# Run standalone (for a quick manual check):  python server.py
# Normally you don't run it directly — trip_agent launches it over stdio.

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("trip-planner")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes -> short human-readable description.
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}


@mcp.tool()
def geocode(place: str) -> dict:
    """Look up the latitude, longitude, and country for a place name.

    This is the first step for any trip question — get_weather needs the
    coordinates this returns. Returns an error dict if the place isn't found.
    """
    with httpx.Client(timeout=15.0) as http:
        resp = http.get(GEOCODING_URL, params={"name": place, "count": 1})
        resp.raise_for_status()
        results = resp.json().get("results")
    if not results:
        return {"error": f"Could not find a location matching {place!r}."}
    top = results[0]
    return {
        "name": top["name"],
        "country": top.get("country"),
        "latitude": top["latitude"],
        "longitude": top["longitude"],
    }


@mcp.tool()
def get_weather(latitude: float, longitude: float, days: int = 3) -> dict:
    """Get current conditions plus a short daily forecast for a lat/lon.

    Use the coordinates returned by `geocode`. `days` is clamped to 1-7.
    Returns current temperature/conditions and a per-day high/low/conditions list.
    """
    days = max(1, min(int(days), 7))
    with httpx.Client(timeout=15.0) as http:
        resp = http.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "daily": "weathercode,temperature_2m_max,temperature_2m_min",
                "forecast_days": days,
                "timezone": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current_weather", {})
    daily = data.get("daily", {})
    forecast = [
        {
            "date": date,
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "conditions": WEATHER_CODES.get(daily["weathercode"][i], f"code {daily['weathercode'][i]}"),
        }
        for i, date in enumerate(daily.get("time", []))
    ]
    return {
        "current": {
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "conditions": WEATHER_CODES.get(current.get("weathercode"), "unknown"),
        },
        "forecast": forecast,
    }


@mcp.tool()
def suggest_packing(temp_max_c: float, temp_min_c: float, conditions: str) -> dict:
    """Suggest what to pack given a temperature range and weather conditions.

    This is the authoritative packing recommendation — always call it (rather
    than improvising packing advice yourself) once you have the weather, so the
    suggestion is grounded in the actual forecast numbers.
    """
    items: list[str] = []

    if temp_min_c <= 0:
        items += ["heavy winter coat", "thermal base layers", "insulated gloves", "warm hat"]
    elif temp_min_c < 10:
        items += ["warm jacket", "sweater/fleece", "long trousers"]
    elif temp_max_c >= 30:
        items += ["lightweight breathable clothing", "sun hat", "sunglasses", "sunscreen"]
    elif temp_max_c >= 22:
        items += ["light layers", "t-shirts", "a light jacket for evenings"]
    else:
        items += ["mixed layers", "a light sweater", "comfortable trousers"]

    cond = conditions.lower()
    if any(w in cond for w in ("rain", "drizzle", "shower", "thunder")):
        items += ["waterproof jacket", "compact umbrella"]
    if any(w in cond for w in ("snow",)):
        items += ["waterproof boots"]

    daily_range = f"{temp_min_c:.0f}-{temp_max_c:.0f}°C"
    summary = f"Expect {daily_range} with {conditions}. Pack for this range."
    return {"summary": summary, "items": items}


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
