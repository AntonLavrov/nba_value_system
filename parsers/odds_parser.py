# parsers/odds_parser.py

import json
from typing import Dict


def load_odds(path: str = "data/raw_odds.json") -> Dict[str, Dict[str, float]]:
    """
    Загружает коэффициенты на матчи.

    Формат raw_odds.json:

    {
      "12345": {
         "home": 1.70,
         "away": 2.20
      }
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    odds = {}

    for game_id, entry in raw.items():
        odds[game_id] = {
            "home": float(entry.get("home", 0)),
            "away": float(entry.get("away", 0)),
        }

    return odds
