# core/fatigue_engine.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class FatigueConfig:
    """
    Настройки модели усталости.

    Все значения в "очках", которые потом можно трактовать
    как корректировку спреда / ожидаемого диффа счёта.
    """
    b2b_penalty: float = -2.0         # штраф за back-to-back
    three_in_four_penalty: float = -1.0  # 3 игры за 4 дня
    four_in_six_penalty: float = -1.5    # 4 игры за 6 дней
    rest_day_bonus: float = 0.0          # при 2+ днях отдыха, если хочешь бонус
    max_abs_adjustment: float = 5.0      # защита от экстремумов

    # Пока без travel/timezone, позже можно расширить:
    travel_penalty_per_1000km: float = 0.0
    timezone_penalty_per_hour: float = 0.0


@dataclass
class TeamGame:
    """
    Универсальное представление игры для одной команды.
    Если твоя структура отличается — адаптируй маппинг в вызове.
    """
    game_id: str
    team: str
    game_date: date


def _compute_games_in_window(
    dates: List[date],
    idx: int,
    window_days: int,
) -> int:
    """
    Сколько игр было у команды в заданное окно (включая текущую)?
    Например, window_days=4 -> 3-in-4, window_days=6 -> 4-in-6.
    """
    current = dates[idx]
    from_date = current - timedelta(days=window_days - 1)
    count = 0
    j = idx
    while j >= 0 and dates[j] >= from_date:
        count += 1
        j -= 1
    return count


def compute_fatigue_for_team_games(
    games: Iterable[TeamGame],
    config: Optional[FatigueConfig] = None,
) -> Dict[Tuple[str, str], float]:
    """
    Главная функция: считает показатель усталости для каждой
    (team, game_id).

    Возвращает словарь:
        {(team, game_id): fatigue_adjustment}
    """
    if config is None:
        config = FatigueConfig()

    # Группируем игры по командам и сортируем по дате
    by_team: Dict[str, List[TeamGame]] = {}
    for g in games:
        by_team.setdefault(g.team, []).append(g)

    for team, team_games in by_team.items():
        team_games.sort(key=lambda x: x.game_date)

    result: Dict[Tuple[str, str], float] = {}

    for team, team_games in by_team.items():
        dates = [g.game_date for g in team_games]

        for idx, game in enumerate(team_games):
            adj = 0.0

            # rest_days: разница с прошлой игрой
            if idx > 0:
                prev_date = dates[idx - 1]
                rest_days = (game.game_date - prev_date).days
            else:
                rest_days = 5  # условно "много отдыха" перед первой игрой

            # B2B
            if rest_days == 1:
                adj += config.b2b_penalty

            # 3-in-4
            games_last_4 = _compute_games_in_window(dates, idx, 4)
            if games_last_4 >= 3:
                adj += config.three_in_four_penalty

            # 4-in-6
            games_last_6 = _compute_games_in_window(dates, idx, 6)
            if games_last_6 >= 4:
                adj += config.four_in_six_penalty

            # бонус за хороший отдых (по желанию)
            if rest_days >= 3 and config.rest_day_bonus != 0.0:
                adj += config.rest_day_bonus

            # travel / timezone потом можно добавить здесь

            # ограничим по модулю
            if abs(adj) > config.max_abs_adjustment:
                adj = config.max_abs_adjustment * (1 if adj > 0 else -1)

            result[(team, game.game_id)] = adj

    return result
