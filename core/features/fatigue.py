# core/features/fatigue.py

from __future__ import annotations
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple
from core.context import GameContext

# ========================================
# CONFIGURATION
# ========================================

@dataclass
class FatigueConfig:
    b2b_penalty: float = -2.0
    three_in_four_penalty: float = -1.0
    four_in_six_penalty: float = -1.5
    rest_bonus: float = 0.0              # бонус если ≥3 дней отдыха
    max_abs_adjustment: float = 5.0


# ========================================
# INTERNAL HELPERS
# ========================================

def count_games_in_window(dates: List[date], idx: int, days: int) -> int:
    """
    Считает сколько игр команда сыграла
    за последние N дней включая текущий матч.
    """
    current = dates[idx]
    since = current - timedelta(days=days - 1)

    count = 0
    j = idx
    while j >= 0 and dates[j] >= since:
        count += 1
        j -= 1

    return count


# ========================================
# MAIN FATIGUE PROCESSOR
# ========================================

class FatigueModule:
    """
    Полноценный модуль усталости.
    Не использует заглушки — считается по расписанию.
    """

    def __init__(self, config: FatigueConfig = None):
        self.cfg = config or FatigueConfig()

        # ❗ Кеш расписания всех команд за сезон:
        # { "LAL": [date1, date2, date3, ...] }
        self.team_schedules: Dict[str, List[date]] = {}

    # -------------------------------------------------------

    def load_schedule(self, schedule: Dict[str, List[date]]):
        """
        schedule — словарь:
        {
            "LAL": [2023-10-21, 2023-10-23, ...],
            "GSW": [...],
        }
        """
        self.team_schedules = schedule

    # -------------------------------------------------------

    def compute_team_fatigue(self, team: str, game_date: date) -> float:

        if team not in self.team_schedules:
            return 0.0

        dates = self.team_schedules[team]
        dates = sorted(dates)

        # ищем индекс текущей игры
        try:
            idx = dates.index(game_date)
        except ValueError:
            return 0.0

        # --- предыдущий матч ---
        if idx > 0:
            rest_days = (dates[idx] - dates[idx - 1]).days
        else:
            rest_days = 5  # старт сезона

        fatigue = 0.0

        # ----------------------------------------------------
        # B2B
        # ----------------------------------------------------
        if rest_days == 1:
            fatigue += self.cfg.b2b_penalty

        # ----------------------------------------------------
        # 3-in-4
        # ----------------------------------------------------
        last_4 = count_games_in_window(dates, idx, 4)
        if last_4 >= 3:
            fatigue += self.cfg.three_in_four_penalty

        # ----------------------------------------------------
        # 4-in-6
        # ----------------------------------------------------
        last_6 = count_games_in_window(dates, idx, 6)
        if last_6 >= 4:
            fatigue += self.cfg.four_in_six_penalty

        # ----------------------------------------------------
        # бонус за отдых
        # ----------------------------------------------------
        if rest_days >= 3:
            fatigue += self.cfg.rest_bonus

        # ограничиваем экстремумы
        if abs(fatigue) > self.cfg.max_abs_adjustment:
            fatigue = self.cfg.max_abs_adjustment * (1 if fatigue > 0 else -1)

        return fatigue

    # -------------------------------------------------------

    def process(self, context: GameContext):
        """
        Основной метод модуля, вызываемый pipeline.
        """

        # данные должны быть загружены заранее
        if not self.team_schedules:
            raise ValueError("FatigueModule: team_schedules not loaded!")

        home_fatigue = self.compute_team_fatigue(context.home, context.date)
        away_fatigue = self.compute_team_fatigue(context.away, context.date)

        context.add_feature("fatigue_home", home_fatigue)
        context.add_feature("fatigue_away", away_fatigue)
