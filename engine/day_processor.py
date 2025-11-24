from parsers.odds_parser import load_odds, save_raw_odds
from parsers.injury_parser import load_injuries, save_injuries
from engine.game_processor import process_game


def extract_injuries(raw_injuries):
    """Преобразуем структуру ESPN под нужный формат"""
    teams = {}

    for item in raw_injuries.get("injuries", []):
        team = item["team"]["displayName"]

        if team not in teams:
            teams[team] = []

        for p in item.get("injuries", []):
            player_role = "starter" if "starter" in p["status"].lower() else "role"

            teams[team].append({
                "name": p["athlete"]["displayName"],
                "role": player_role
            })

    return teams


def run_day():
    print("=== Загрузка линий ===")
    odds = load_odds()
    save_raw_odds(odds)

    print("=== Загрузка травм ===")
    injuries_raw = load_injuries()
    save_injuries(injuries_raw)

    injuries = extract_injuries(injuries_raw)

    print("=== Анализ матчей дня ===")

    results = []

    for game in odds:
        result = process_game(game, injuries)
        results.append(result)

    print("\n=== ВСЕ МАТЧИ ПРОАНАЛИЗИРОВАНЫ ===")

    return results
