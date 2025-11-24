# run_daily.py

from parsers.schedule_parser import load_schedule_for_today
from parsers.ratings_parser import load_team_ratings
from parsers.injury_parser import load_injuries
from parsers.odds_parser import load_odds

from engine.day_processor import DayProcessor
from core.export.export_json import export_to_json
from core.export.export_xlsx import export_to_excel


def run():
    # 1. Загружаем данные
    games = load_schedule_for_today()
    ratings = load_team_ratings()
    injuries = load_injuries()
    odds = load_odds()

    # 2. Добавляем данные в игры
    for game in games:
        game.rating_home = ratings.get(game.home, 0)
        game.rating_away = ratings.get(game.away, 0)

        game.odds = odds.get(game.id, {})
        game.injuries_home = injuries.get(game.home, [])
        game.injuries_away = injuries.get(game.away, [])

    # 3. Обрабатываем день
    dp = DayProcessor()
    contexts = dp.process_day(games)

    # 4. Экспортируем результаты
    export_to_json(contexts, "outputs/value_today.json")
    export_to_excel(contexts, "outputs/value_today.xlsx")

    print("✔ Готово: обработано игр =", len(contexts))


if __name__ == "__main__":
    run()
