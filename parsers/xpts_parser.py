# parsers/xpts_parser.py

import json
from typing import Dict, Any


def load_team_xpts(path: str = "data/team_xpts.json") -> Dict[str, Dict[str, float]]:
    """
    Загружает ожидаемые очки (xPTS) команд.

    Ожидаемый формат data/team_xpts.json:

    {
      "LAL": {
        "off_xpts_per_game": 115.2,
        "def_xpts_per_game": 112.3
      },
      "GSW": {
        "off_xpts_per_game": 113.1,
        "def_xpts_per_game": 111.0
      }
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    result: Dict[str, Dict[str, float]] = {}

    for team, vals in raw.items():
        off_val = vals.get("off_xpts_per_game", None)
        def_val = vals.get("def_xpts_per_game", None)
        try:
            off_x = float(off_val) if off_val is not None else None
            def_x = float(def_val) if def_val is not None else None
        except (TypeError, ValueError):
            off_x, def_x = None, None

        result[team] = {
            "off_xpts_per_game": off_x if off_x is not None else 0.0,
            "def_xpts_per_game": def_x if def_x is not None else 0.0,
        }

    return result
