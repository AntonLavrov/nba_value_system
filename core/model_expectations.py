LEAGUE_AVG_PACE = 98.0


def calc_xpts(
    team_or,
    team_dr,
    opp_or,
    opp_dr,
    pace_team,
    pace_opp,
    home: bool = False,
    motivation: float = 0.0,
    fatigue: float = 0.0
):
    """
    team_or / team_dr — рейтинги команды
    opp_or / opp_dr — рейтинги соперника
    pace_team / pace_opp — темпы команд
    home — флаг домашней команды
    motivation — +очки за мотивацию (must-win и т.д.)
    fatigue — -очки за усталость (B2B, 3/4 и т.д.)
    """

    base = (team_or + opp_dr) / 2

    # корректировка на темп
    pace = (pace_team + pace_opp) / 2
    pace_factor = pace / LEAGUE_AVG_PACE
    pts = base * pace_factor

    # домашний корт
    if home:
        pts += 2.5

    # мотивация (положительная)
    pts += motivation

    # усталость (как правило отрицательная)
    pts += fatigue

    return pts
