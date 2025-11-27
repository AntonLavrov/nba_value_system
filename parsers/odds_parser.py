import json
from typing import Dict, Any


def load_odds(path: str = "data/raw_odds.json") -> Dict[str, Dict[str, Any]]:
    """
    Загружает коэффициенты и линии на матчи из JSON.

    Ожидаемый формат raw_odds.json (пример):

    {
      "12345": {
        "home": 1.70,
        "away": 2.10,

        "spread_line": -4.5,
        "spread_odds_home": 1.91,
        "spread_odds_away": 1.91,

        "total_line": 226.5,
        "total_over_odds": 1.9,
        "total_under_odds": 1.9,

        "home_team_total": 115.5,
        "home_team_total_over_odds": 1.9,
        "home_team_total_under_odds": 1.9,

        "away_team_total": 111.5,
        "away_team_total_over_odds": 1.9,
        "away_team_total_under_odds": 1.9
      }
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    odds: Dict[str, Dict[str, Any]] = {}

    for game_id, entry in raw.items():
        record: Dict[str, Any] = {}

        # Moneyline
        for key in ("home", "away"):
            if key in entry:
                try:
                    record[key] = float(entry[key])
                except (TypeError, ValueError):
                    continue

        # Spread
        for key in ("spread_line", "spread_odds_home", "spread_odds_away"):
            if key in entry:
                try:
                    record[key] = float(entry[key])
                except (TypeError, ValueError):
                    continue

        # Total
        for key in ("total_line", "total_over_odds", "total_under_odds"):
            if key in entry:
                try:
                    record[key] = float(entry[key])
                except (TypeError, ValueError):
                    continue

        # Team totals
        for key in (
            "home_team_total",
            "home_team_total_over_odds",
            "home_team_total_under_odds",
            "away_team_total",
            "away_team_total_over_odds",
            "away_team_total_under_odds",
        ):
            if key in entry:
                try:
                    record[key] = float(entry[key])
                except (TypeError, ValueError):
                    continue

        odds[game_id] = record

    return odds


# На случай, если где-то в коде использовалось старое имя
def parse_odds(path: str = "data/raw_odds.json") -> Dict[str, Dict[str, Any]]:
    return load_odds(path)
