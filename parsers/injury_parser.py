# parsers/injury_parser.py

import json
from typing import Dict, List


def load_injuries(path: str = "data/injuries_today.json") -> Dict[str, List[str]]:
    """
    Загружает список травм.

    Формат injuries_today.json:
    {
      "LAL": ["LeBron James"],
      "GSW": ["Stephen Curry", "Klay Thompson"]
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    injuries = {}

    for team, players in data.items():
        if isinstance(players, list):
            injuries[team] = players
        else:
            injuries[team] = []

    return injuries
