# core/features/fatigue.py

from core.context import GameContext
from datetime import timedelta

class FatigueModule:
    def __init__(self):
        self.b2b_penalty = -2.0
        self.three_in_four_penalty = -1.0
        self.four_in_six_penalty = -1.5

    def process(self, context: GameContext):
        # context.add_feature(...)
        # Здесь позже я подключу твой реальный расписание-парсер
        context.add_feature("fatigue_home", 0.0)
        context.add_feature("fatigue_away", 0.0)
