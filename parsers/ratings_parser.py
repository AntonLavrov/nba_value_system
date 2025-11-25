# parsers/ratings_parser.py

import json
from typing import Dict


def load_team_ratings(path: str = "data/team_ratings.json") -> Dict[str, float]:
    """
    Загружает рейтинги команд.
    Возвращает: { "LAL": 3.2, "GSW": 1.9 }
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    ratings = {}

    for team, value in raw.items():
        try:
            ratings[team] = float(value)
        except (TypeError, ValueError):
            ratings[team] = 0.0

    return ratings
