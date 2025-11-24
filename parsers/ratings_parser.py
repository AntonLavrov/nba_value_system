import json
import os
from config import DATA_FOLDER

RATINGS_PATH = os.path.join(DATA_FOLDER, "team_ratings.json")

DEFAULT_RATING = {"ORtg": 115.0, "DRtg": 115.0, "Pace": 98.0}


def load_team_ratings():
    try:
        with open(RATINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Не найден {RATINGS_PATH}, используются дефолтные рейтинги.")
        return {}


TEAM_RATINGS = load_team_ratings()


def get_team_rating(team_name: str):
    """
    Возвращает словарь с ORtg/DRtg/Pace для команды.
    Если команда не найдена — дефолт.
    """
    return TEAM_RATINGS.get(team_name, DEFAULT_RATING)
