# engine/day_processor.py

from __future__ import annotations
from typing import List

from engine.game_processor import GameProcessor
from core.context import GameContext


class DayProcessor:
    """
    Обработка игрового дня целиком.

    - На вход: список объектов Game (из run_daily.py)
    - На выход: список GameContext с рассчитанными фичами и моделями
    """

    def __init__(self):
        self.game_processor = GameProcessor()

    def process_day(self, games: List[object]) -> List[GameContext]:
        """
        Обрабатывает все игры дня.

        games — список объектов, у которых есть:
            .id
            .date
            .home
            .away
            (и дополнительные атрибуты: rating_home, injuries, odds)
        """
        results: List[GameContext] = []

        for game in games:
            ctx = self.game_processor.process(game)
            results.append(ctx)

        return results
print("DEBUG RESULT:", result)
