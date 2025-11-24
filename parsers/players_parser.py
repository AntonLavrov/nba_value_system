# parsers/players_parser.py

import json
from typing import Dict


def load_player_impacts(path: str = "data/players.json") -> Dict[str, Dict[str, float]]:
    """
    Загружает 'силу' игроков в очках для каждой команды.

    Формат файла:
    {
        "LAL": {
            "LeBron James": 4.5,
            "Anthony Davis": 3.8
        },
        "GSW": {
            "Stephen Curry": 5.0
        }
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # простая валидация
    result: Dict[str, Dict[str, float]] = {}
    for team, players in data.items():
        team_dict: Dict[str, float] = {}
        for name, impact in players.items():
            try:
                team_dict[name] = float(impact)
            except (TypeError, ValueError):
                continue
        result[team] = team_dict

    return result
