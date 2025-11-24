# core/features/pace.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from core.context import GameContext
from parsers.pace_parser import load_team_pace


@dataclass
class PaceConfig:
    """
    Настройки для модуля темпа.
    """
    default_pace: float = 99.0        # если для команды нет данных
    league_avg_pace: float = 99.0     # средний темп по лиге (для нормировки)
    max_pace: float = 110.0
    min_pace: float = 90.0


class PaceModule:
    """
    Модуль, который оценивает ожидаемый темп матча (pace).

    - Использует pace команд (possessions per game).
    - Считает гармоническое среднее для матча.
    """

    def __init__(self, config: PaceConfig | None = None):
        self.cfg = config or PaceConfig()
        # словарь: { "LAL": 101.3, "GSW": 100.1, ... }
        self.team_pace: Dict[str, float] = load_team_pace()

    def _get_team_pace(self, team: str) -> float:
        pace = self.team_pace.get(team, self.cfg.default_pace)
        if pace < self.cfg.min_pace:
            pace = self.cfg.min_pace
        if pace > self.cfg.max_pace:
            pace = self.cfg.max_pace
        return pace

    def _harmonic_mean(self, a: float, b: float) -> float:
        if a <= 0 or b <= 0:
            return self.cfg.league_avg_pace
        return 2 * (a * b) / (a + b)

    def process(self, context: GameContext):
        """
        Основной метод, вызываемый пайплайном.
        """

        pace_home = self._get_team_pace(context.home)
        pace_away = self._get_team_pace(context.away)

        pace_match = self._harmonic_mean(pace_home, pace_away)

        context.add_feature("pace_home", pace_home)
        context.add_feature("pace_away", pace_away)
        context.add_feature("pace_match", pace_match)
        context.add_feature("league_avg_pace", self.cfg.league_avg_pace)
