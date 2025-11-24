# parsers/standings_parser.py

import json
from typing import Dict, Any


def load_standings(path: str = "data/standings.json") -> Dict[str, Dict[str, Any]]:
    """
    Загружает турнирное положение команд.

    Ожидаемый формат data/standings.json:

    {
      "LAL": {
        "conference_rank": 8,
        "wins": 42,
        "losses": 39
      },
      "DEN": {
        "conference_rank": 1,
        "wins": 55,
        "losses": 26
      }
    }

    Минимум нужен conference_rank.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    result: Dict[str, Dict[str, Any]] = {}
    for team, info in raw.items():
        try:
            rank = int(info.get("conference_rank", 0))
        except (TypeError, ValueError):
            rank = 0
        result[team] = {
            "conference_rank": rank,
            "wins": int(info.get("wins", 0)),
            "losses": int(info.get("losses", 0)),
        }

    return result
