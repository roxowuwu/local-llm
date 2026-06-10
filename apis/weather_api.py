import requests
from collections import defaultdict
from datetime import datetime


class WeatherController:

    def __init__(self, prefs: dict):
        weather_cfg = prefs.get("weather", {})

        self.api_key = weather_cfg.get("api_key")
        self.default_city = weather_cfg.get("city", "Delhi")

        self.base_url = "https://api.openweathermap.org/data/2.5"

    # -----------------------------
    # CURRENT WEATHER
    # -----------------------------
    def get_current(self, city: str = None) -> dict:
        city = city or self.default_city

        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            res = requests.get(url, params=params)
        except Exception:
            raise ConnectionError("Network error")

        if res.status_code == 404:
            raise ValueError("City not found")

        data = res.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "humidity_pct": data["main"]["humidity"],
            "wind_kmh": round(data["wind"]["speed"] * 3.6, 1)
        }

    # -----------------------------
    # FORECAST
    # -----------------------------
    def get_forecast(self, city: str = None, days: int = 3):
        city = city or self.default_city
        days = min(days, 5)

        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            res = requests.get(url, params=params)
        except Exception:
            raise ConnectionError("Network error")

        if res.status_code == 404:
            raise ValueError("City not found")

        data = res.json()

        daily = defaultdict(list)

        for item in data["list"]:
            date = item["dt_txt"].split()[0]
            daily[date].append(item)

        results = []

        for date, entries in list(daily.items())[:days]:
            temps = [e["main"]["temp"] for e in entries]

            results.append({
                "date": date,
                "min_temp": round(min(temps), 1),
                "max_temp": round(max(temps), 1),
                "condition": entries[0]["weather"][0]["main"],
                "description": entries[0]["weather"][0]["description"]
            })

        return results

    # -----------------------------
    # FORMAT CURRENT
    # -----------------------------
    def format_current(self, data: dict) -> str:
        return (
            f"{data['city']}: {data['temp_c']}°C, feels like {data['feels_like_c']}°C\n"
            f"Condition: {data['condition']} ({data['description']})\n"
            f"Humidity: {data['humidity_pct']}% | Wind: {data['wind_kmh']} km/h"
        )

    # -----------------------------
    # FORMAT FORECAST
    # -----------------------------
    def format_forecast(self, data: list) -> str:
        lines = []

        for day in data:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            day_name = date_obj.strftime("%a")

            lines.append(
                f"{day_name}: {day['min_temp']}-{day['max_temp']}°C, {day['condition']}"
            )

        return "\n".join(lines)
