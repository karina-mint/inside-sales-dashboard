"""Example function with weather data retrieval."""
from typing import Protocol
import httpx
from agents import function_tool


class WeatherClient(Protocol):
    """Weather API client protocol."""

    async def get_weather(self, city: str) -> dict:
        """Fetch weather data."""
        ...


class OpenMeteoWeatherClient:
    """Open-Meteo API based weather client."""

    def __init__(self):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    async def get_weather(self, city: str) -> dict:
        """Fetch weather data from Open-Meteo API."""
        async with httpx.AsyncClient() as client:
            # 都市名から緯度経度を取得
            geo_response = await client.get(
                self.geocoding_url,
                params={"name": city, "count": 1, "language": "ja"},
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                raise ValueError(f"City not found: {city}")

            location = geo_data["results"][0]
            latitude = location["latitude"]
            longitude = location["longitude"]

            # 天気情報を取得
            weather_response = await client.get(
                self.weather_url,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": "true",
                },
            )
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            current = weather_data["current_weather"]
            return {
                "city": city,
                "temperature": current["temperature"],
                "condition": self._get_weather_description(current["weathercode"]),
            }

    def _get_weather_description(self, code: int) -> str:
        """WMO Weather interpretation codes を日本語に変換."""
        descriptions = {
            0: "快晴",
            1: "晴れ",
            2: "一部曇り",
            3: "曇り",
            45: "霧",
            48: "霧氷",
            51: "小雨",
            53: "雨",
            55: "大雨",
            61: "小雨",
            63: "雨",
            65: "大雨",
            71: "小雪",
            73: "雪",
            75: "大雪",
            80: "にわか雨",
            81: "にわか雨",
            82: "強いにわか雨",
            95: "雷雨",
            96: "雷雨と雹",
            99: "雷雨と雹",
        }
        return descriptions.get(code, f"不明 (コード: {code})")


async def get_weather_data_impl(city: str, client=None) -> dict:
    """Get weather data for a city (implementation).

    Args:
        city: City name
        client: Optional weather client (defaults to OpenMeteoWeatherClient)

    Returns:
        Weather data including temperature and condition
    """
    if client is None:
        client = OpenMeteoWeatherClient()
    return await client.get_weather(city)


@function_tool
async def get_weather_data(city: str) -> dict:
    """Get weather data for a city.

    Args:
        city: City name

    Returns:
        Weather data including temperature and condition
    """
    return await get_weather_data_impl(city)
