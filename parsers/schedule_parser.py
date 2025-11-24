def load_full_season_schedule():
    """
    Возвращает словарь:
    {
        "LAL": [date1, date2, ...],
        "GSW": [...]
    }
    """
    import json
    from datetime import datetime

    with open("data/schedule.json", "r") as f:
        raw = json.load(f)

    schedule = {}

    for game in raw:
        d = datetime.strptime(game["date"], "%Y-%m-%d").date()

        for team in (game["home"], game["away"]):
            schedule.setdefault(team, []).append(d)

    return schedule
