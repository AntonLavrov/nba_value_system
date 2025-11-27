# run_daily.py

import json
from datetime import datetime
from data.game_object import Game
from engine.game_processor import GameProcessor
from parsers.odds_parser import load_odds

def load_schedule_for_fatigue(path="data/schedule.json"):
    """
    Формирует словарь:
    {
      "LAL": [date1, date2, ...],
      "GSW": [...],
      ...
    }
    """
    from datetime import datetime
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    schedules = {}

    for entry in raw:
        d = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        home = entry["home"]
        away = entry["away"]

        schedules.setdefault(home, []).append(d)
        schedules.setdefault(away, []).append(d)

    return schedules


def run_daily():

    print("======================================")
    print("     NBA VALUE SYSTEM — DAILY RUN     ")
    print("======================================")

    # --------------------------------------
    # Load schedule_today
    # --------------------------------------
    print("Загрузка расписания...")
    with open("data/schedule_today.json", "r", encoding="utf-8") as f:
        games_today = json.load(f)

    print(f"Матчей найдено: {len(games_today)}")

    # --------------------------------------
    # Load ratings
    # --------------------------------------
    print("Загрузка рейтингов...")
    ratings = {}
    try:
        with open("data/team_ratings.json", "r", encoding="utf-8") as f:
            ratings = json.load(f)
    except:
        print("⚠ Нет файла team_ratings.json")

    # --------------------------------------
    # Load injuries
    # --------------------------------------
    print("Загрузка травм...")
    injuries_today = {}
    try:
        with open("data/injuries_today.json", "r", encoding="utf-8") as f:
            injuries_today = json.load(f)
    except:
        print("⚠ Нет injuries_today.json")

    # --------------------------------------
    # Load odds
    # --------------------------------------
    print("Загрузка коэффициентов...")
    odds = load_odds()

    # --------------------------------------
    # Build game objects
    # --------------------------------------
    print("Обогащение объектов игр...")

    game_objects = []

    for g in games_today:
        game = Game(
            id=g["game_id"],
            date=datetime.strptime(g["date"], "%Y-%m-%d").date(),
            home=g["home"],
            away=g["away"]
        )

        game.rating_home = ratings.get(game.home, 100)
        game.rating_away = ratings.get(game.away, 100)

        game.injuries_home = injuries_today.get(game.home, [])
        game.injuries_away = injuries_today.get(game.away, [])

        game.odds = odds.get(g["game_id"], {})

        game_objects.append(game)

    # --------------------------------------
    # GameProcessor
    # --------------------------------------
    print("Создание GameProcessor...")
    processor = GameProcessor()

    # --------------------------------------
    # Load fatigue schedule
    # --------------------------------------
    print("Загрузка расписания для FatigueModule...")
    schedule_for_fatigue = load_schedule_for_fatigue("data/schedule.json")
    processor.fatigue.load_schedule(schedule_for_fatigue)

    # --------------------------------------
    # Run models
    # --------------------------------------
    print("Запуск модели...")

    contexts = []

    for game in game_objects:
        ctx = processor.process(game)
        contexts.append(ctx)

    # --------------------------------------
    # Exporters (names fixed)
    # --------------------------------------
    print("Сохранение результатов...")

    from core.export.export_json import export_to_json
    from core.export.export_html import export_to_html
    from core.export.export_xlsx import export_to_xlsx

    export_to_json(contexts, "outputs/value_today.json")
    export_to_html(contexts, "outputs/value_today.html")
    export_to_xlsx(contexts, "outputs/value_today.xlsx")

    print("Готово!")


if __name__ == "__main__":
    run_daily()
