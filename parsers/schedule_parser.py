# parsers/schedule_parser.py

import json
from datetime import datetime
from typing import Dict, List


def load_full_season_schedule(path: str = "data/schedule.json") -> Dict[str, List[datetime.date]]:
    """
    Загружает полное расписание для FatigueModule.

    Формат schedule.json:
    [
      {"date": "2024-01-02", "home": "LAL", "away": "GSW"},
      ...
    ]

    Возвращает:
    {
      "LAL": [date1, date2, ...],
      "GSW": [...],
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        games = json.load(f)

    schedule = {}

    for g in games:
        d = datetime.strptime(g["date"], "%Y-%m-%d").date()
        home = g["home"]
        away = g["away"]

        schedule.setdefault(home, []).append(d)
        schedule.setdefault(away, []).append(d)

    # сортируем даты
    for team in schedule:
        schedule[team].sort()

    return schedule


def load_games_today(path: str = "data/schedule_today.json") -> List[dict]:
    """
    Загружает список игр на сегодня.
    Формат schedule_today.json:

    [
      {"game_id": "12345", "date": "2024-01-02", "home": "LAL", "away": "GSW"},
      ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
