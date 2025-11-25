# run_daily.py

import json
from datetime import datetime

from engine.game_processor import GameProcessor

from parsers.schedule_parser import load_games_today
from parsers.ratings_parser import load_team_ratings
from parsers.injury_parser import load_injuries
from parsers.odds_parser import load_odds

from core.export.export_json import export_to_json
from core.export.export_xlsx import export_to_xlsx
from core.export.export_html import export_to_html


class Game:
    """Простой объект матча, который передаётся в GameProcessor."""
    def __init__(self, game_id, date, home, away):
        self.id = game_id
        self.date = date
        self.home = home
        self.away = away


def run_daily():
    print("=== Запуск ежедневной модели NBA ===")

    # -----------------------------------------------
    # Загрузка данных
    # -----------------------------------------------
    print("Загрузка рейтингов команд...")
    team_ratings = load_team_ratings()

    print("Загрузка травм...")
    injuries = load_injuries()

    print("Загрузка коэффициентов...")
    odds = load_odds()

    print("Загрузка расписания на сегодня...")
    schedule_today = load_games_today()

    # -----------------------------------------------
    # Создаём список объектов Game
    # -----------------------------------------------
    games = []
    for entry in schedule_today:
        game_id = entry["game_id"]
        date = entry["date"]
        home = entry["home"]
        away = entry["away"]

        g = Game(
            game_id=game_id,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            home=home,
            away=away
        )

        # добавляем рейтинги
        g.rating_home = team_ratings.get(home, 0.0)
        g.rating_away = team_ratings.get(away, 0.0)

        # травмы
        g.injuries_home = injuries.get(home, [])
        g.injuries_away = injuries.get(away, [])

        # коэффициенты
        g.odds = odds.get(game_id, {})

        games.append(g)

    # -----------------------------------------------
    # Запуск обработки всех игр
    # -----------------------------------------------
    processor = GameProcessor()
    results = []

    print("Обработка игр:")
    for game in games:
        print(f"  → {game.home} vs {game.away}")
        ctx = processor.process(game)
        results.append(ctx)

    # -----------------------------------------------
    # Экспорт результатов
    # -----------------------------------------------
    print("Сохранение результатов...")

    export_to_json(results, "outputs/value_today.json")
    export_to_xlsx(results, "outputs/value_today.xlsx")
    export_to_html(results, "outputs/value_today.html")

    print("Готово! Результаты сохранены в outputs/.")


if __name__ == "__main__":
    run_daily()
