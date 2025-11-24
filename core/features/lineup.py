# core/features/lineup.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from core.context import GameContext
from parsers.players_parser import load_player_impacts


@dataclass
class LineupConfig:
    """
    Конфиг для Lineup Engine.
    """
    max_abs_adjustment: float = 10.0  # защита от экстремумов
    unknown_injury_penalty: float = 0.5  # штраф, если игрок не найден в списке, но травмирован


class LineupModule:
    """
    Модуль, который переводит травмы и силу игроков
    в очковую корректировку для команды.
    """

    def __init__(self, config: LineupConfig | None = None):
        self.cfg = config or LineupConfig()
        # { "LAL": { "LeBron James": 4.5, ... }, ... }
        self.player_impacts: Dict[str, Dict[str, float]] = load_player_impacts()

    # -----------------------------------------------------

    def _compute_team_lineup_adjustment(self, team: str, injured_players: List[str]) -> float:
        """
        Считает, сколько очков команда теряет из-за травм.
        Положим, что травма LeBron с impact=4.5 значит
        -4.5 очка к силе команды.
        """
        if not injured_players:
            return 0.0

        team_players = self.player_impacts.get(team, {})
        total_impact = 0.0

        for name in injured_players:
            if name in team_players:
                total_impact -= team_players[name]  # отсутствие = минус к силе
            else:
                # если не знаем игрока, но травма есть — небольшой штраф
                total_impact -= self.cfg.unknown_injury_penalty

        # ограничим экстремумы
        if abs(total_impact) > self.cfg.max_abs_adjustment:
            total_impact = self.cfg.max_abs_adjustment * (1 if total_impact > 0 else -1)

        return total_impact

    # -----------------------------------------------------

    def process(self, context: GameContext):
        """
        Основной вызов модуля из pipeline.
        Ожидает, что в context.features лежат:
         - injuries_home: List[str]
         - injuries_away: List[str]
        """

        injuries_home = context.features.get("injuries_home", [])
        injuries_away = context.features.get("injuries_away", [])

        if not isinstance(injuries_home, list):
            injuries_home = []
        if not isinstance(injuries_away, list):
            injuries_away = []

        home_adj = self._compute_team_lineup_adjustment(context.home, injuries_home)
        away_adj = self._compute_team_lineup_adjustment(context.away, injuries_away)

        # lineup_home / lineup_away — это именно корректировка в очках
        context.add_feature("lineup_home", home_adj)
        context.add_feature("lineup_away", away_adj)
