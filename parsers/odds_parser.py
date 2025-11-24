import requests
import json
from config import ODDS_API_KEY, ODDS_API_REGION, ODDS_API_MARKETS


def load_odds():
    """Загружает линии NBA через The Odds API"""
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": ODDS_API_REGION,
        "markets": ",".join(ODDS_API_MARKETS),
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data


def save_raw_odds(data, path="data/raw_odds.json"):
    """Сохраняет сырые линии в JSON"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
