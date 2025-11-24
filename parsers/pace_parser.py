# parsers/pace_parser.py

import json
from typing import Dict


def load_team_pace(path: str = "data/team_pace.json") -> Dict[str, float]:
    """
    Загружает темп (pace) команд из JSON.

    Ожидаемый формат файла data/team_pace.json:

    {
      "LAL": 101.3,
      "GSW": 100.1,
      "DEN": 97.8
    }

    Где значение — possessions per game.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    result: Dict[str, float] = {}
    for team, val in raw.items():
        try:
            result[team] = float(val)
        except (TypeError, ValueError):
            continue

    return result
