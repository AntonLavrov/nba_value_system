import requests
import json


def load_injuries():
    """Парсер травм с ESPN API"""
    url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/injuries"

    response = requests.get(url)
    data = response.json()

    return data


def save_injuries(data, path="data/injuries_today.json"):
    """Сохраняем"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
