from core.model_expectations import calc_xpts
from core.model_probabilities import (
    logistic_win_probability,
    probability_total,
    probability_team_total,
)
from core.model_ev import expected_value
from core.injuries import get_player_impact
from parsers.ratings_parser import get_team_rating


# -----------------------
# УЧЁТ ТРАВМ
# -----------------------
def apply_injury_impact(team_name, injuries_list, base_or):
    """
    injuries_list — список травм по команде
    base_or — базовый ORtg
    Возвращает (скорректированный ORtg, суммарный импакт в очках)
    """
    impact_sum = 0.0

    for player in injuries_list:
        role = player.get("role", "role")  # star / starter / role
        imp = get_player_impact(role)
        impact_sum += imp

    return base_or + impact_sum, impact_sum


# -----------------------
# МОТИВАЦИЯ / УСТАЛОСТЬ (пока заглушки)
# -----------------------
def estimate_motivation(game_data, team_side: str) -> float:
    """
    Здесь в будущем можно учитывать:
    - must-win (+2..+3)
    - важная игра (+1..+1.5)
    - низкая мотивация (-1..-2)
    Пока возвращаем 0, но поле будет в таблице.
    """
    return 0.0


def estimate_fatigue(game_data, team_side: str) -> float:
    """
    Здесь в будущем можно учитывать:
    - B2B (-1)
    - 3 игры за 4 дня (-1.5)
    - перелёты (-0.5..-1)
    Пока возвращаем 0, поле будет в таблице.
    """
    return 0.0


# -----------------------
# ОБРАБОТКА ОДНОГО МАТЧА
# -----------------------
def process_game(game_data, injuries):
    """
    game_data — один матч из Odds API:
      {
        "home_team": ...,
        "away_team": ...,
        "bookmakers": [ { "markets": [...] }, ... ]
      }

    injuries — словарь вида:
      {
        "Boston Celtics": [ { "name": "...", "role": "star" }, ... ],
        ...
      }

    Возвращает dict с:
    - xPTS, xTOTAL, xMargin, win_prob
    - мотивацией, усталостью, импактом травм
    - всеми value-линиями (value_lines)
    """

    home = game_data["home_team"]
    away = game_data["away_team"]

    print(f"\n=== АНАЛИЗ МАТЧА: {home} vs {away} ===")

    # --- РЕЙТИНГИ КОМАНД ---
    home_rating = get_team_rating(home)
    away_rating = get_team_rating(away)

    home_ORtg_base = home_rating["ORtg"]
    home_DRtg_base = home_rating["DRtg"]
    home_pace = home_rating.get("Pace", 98.0)

    away_ORtg_base = away_rating["ORtg"]
    away_DRtg_base = away_rating["DRtg"]
    away_pace = away_rating.get("Pace", 98.0)

    # --- ТРАВМЫ ---
    home_inj_list = injuries.get(home, [])
    away_inj_list = injuries.get(away, [])

    home_ORtg_final, home_injury_impact = apply_injury_impact(
        home, home_inj_list, home_ORtg_base
    )
    away_ORtg_final, away_injury_impact = apply_injury_impact(
        away, away_inj_list, away_ORtg_base
    )

    # --- МОТИВАЦИЯ / УСТАЛОСТЬ ---
    home_motivation = estimate_motivation(game_data, "home")
    away_motivation = estimate_motivation(game_data, "away")

    home_fatigue = estimate_fatigue(game_data, "home")
    away_fatigue = estimate_fatigue(game_data, "away")

    # --- xPTS ДЛЯ ДОМА ---
    home_xpts = calc_xpts(
        team_or=home_ORtg_final,
        team_dr=home_DRtg_base,
        opp_or=away_ORtg_final,
        opp_dr=away_DRtg_base,
        pace_team=home_pace,
        pace_opp=away_pace,
        home=True,
        motivation=home_motivation,
        fatigue=home_fatigue,
    )

    # --- xPTS ДЛЯ ГОСТЕЙ ---
    away_xpts = calc_xpts(
        team_or=away_ORtg_final,
        team_dr=away_DRtg_base,
        opp_or=home_ORtg_final,
        opp_dr=home_DRtg_base,
        pace_team=away_pace,
        pace_opp=home_pace,
        home=False,
        motivation=away_motivation,
        fatigue=away_fatigue,
    )

    xTOTAL = home_xpts + away_xpts
    xMargin = home_xpts - away_xpts  # home - away

    # --- Вероятность победы дома (логистика NBA) ---
    win_prob = logistic_win_probability(xMargin)

    print(f"Home xPTS: {home_xpts:.2f}")
    print(f"Away xPTS: {away_xpts:.2f}")
    print(f"xTOTAL: {xTOTAL:.2f}")
    print(f"xMargin: {xMargin:.2f}")
    print(f"Вероятность победы {home}: {win_prob * 100:.1f}%")

    # ------------------------------
    # EV ДЛЯ ВСЕХ РЫНКОВ (The Odds API)
    # ------------------------------
    value_lines = []

    for bookmaker in game_data.get("bookmakers", []):
        for market in bookmaker.get("markets", []):

            market_key = market.get("key")      # "h2h" / "spreads" / "totals"
            outcomes = market.get("outcomes", [])

            # ===== ТОТАЛЫ =====
            if market_key == "totals":
                for out in outcomes:
                    side = out.get("name")      # "Over" / "Under"
                    line = out.get("point")     # число тотала
                    price = out.get("price")    # кэф (DECIMAL, мы уже привели в парсере)

                    if line is None or price is None:
                        continue

                    if side == "Over":
                        model_prob = probability_total(
                            xTOTAL, line, side="over"
                        )
                    elif side == "Under":
                        model_prob = probability_total(
                            xTOTAL, line, side="under"
                        )
                    else:
                        continue

                    ev = expected_value(model_prob, price)

                    value_lines.append({
                        "market": "тотал",
                        "side": side,
                        "line": line,
                        "price": price,
                        "model_prob": model_prob,
                        "ev": ev,
                    })

            # ===== ФОРЫ (SPREADS) =====
            elif market_key == "spreads":
                for out in outcomes:
                    team = out.get("name")      # имя команды
                    line = out.get("point")     # форa для этой команды
                    price = out.get("price")    # кэф

                    if team is None or line is None or price is None:
                        continue

                    # Фору интерпретируем через xMargin (home - away)
                    if team == home:
                        model_prob = probability_team_total(
                            xMargin, line, side="home"
                        )
                    elif team == away:
                        model_prob = probability_team_total(
                            xMargin, line, side="away"
                        )
                    else:
                        # Странное имя команды (не совпало) — пропускаем
                        continue

                    ev = expected_value(model_prob, price)

                    value_lines.append({
                        "market": "фора",
                        "team": team,
                        "line": line,
                        "price": price,
                        "model_prob": model_prob,
                        "ev": ev,
                    })

            # ===== MONEYLINE (H2H) =====
            elif market_key == "h2h":
                for out in outcomes:
                    team = out.get("name")
                    price = out.get("price")

                    if team is None or price is None:
                        continue

                    if team == home:
                        prob = win_prob
                    elif team == away:
                        prob = 1 - win_prob
                    else:
                        continue

                    ev = expected_value(prob, price)

                    value_lines.append({
                        "market": "победа",
                        "team": team,
                        "price": price,
                        "model_prob": prob,
                        "ev": ev,
                    })

    # --- Возвращаем расширенный результат по матчу ---
    return {
        "home": home,
        "away": away,

        # базовые рейтинги
        "home_or_base": home_ORtg_base,
        "home_dr_base": home_DRtg_base,
        "away_or_base": away_ORtg_base,
        "away_dr_base": away_DRtg_base,

        # финальные OR после травм
        "home_or_final": home_ORtg_final,
        "away_or_final": away_ORtg_final,

        # импакт травм (в очках)
        "home_injury_impact": home_injury_impact,
        "away_injury_impact": away_injury_impact,

        # мотивация / усталость
        "home_motivation": home_motivation,
        "away_motivation": away_motivation,
        "home_fatigue": home_fatigue,
        "away_fatigue": away_fatigue,

        # модельные ожидания
        "home_xpts": home_xpts,
        "away_xpts": away_xpts,
        "xTOTAL": xTOTAL,
        "xMargin": xMargin,
        "win_prob_home": win_prob,

        # список всех рассчитанных линий
        "value_lines": value_lines,
    }
