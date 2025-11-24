# core/features/xpts.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from core.context import GameContext
from parsers.xpts_parser import load_team_xpts


@dataclass
class XPTSConfig:
    """
    Настройки для использования xPTS.

    По сути, weight — насколько сильно shot quality влияет
    на ожидаемый дифф очков.
    """
    shot_quality_weight: float = 1.0  # коэффициент влияния
    default_off_xpts: float = 112.0
    default_def_xpts: float = 112.0


class XPTSModule:
    """
    Модуль, который добавляет в контекст информацию об ожидаемых
    очках по качеству бросков (xPTS) для нападения и защиты.

    Здесь мы используем заранее подготовленные значения по командам,
    а не считаем их "на лету" по каждым броскам (это отдельная большая задача).
    """

    def __init__(self, config: XPTSConfig | None = None):
        self.cfg = config or XPTSConfig()
        # { "LAL": {"off_xpts_per_game": 115.2, "def_xpts_per_game": 112.3}, ... }
        self.team_xpts: Dict[str, Dict[str, float]] = load_team_xpts()

    def _get_off_xpts(self, team: str) -> float:
        vals = self.team_xpts.get(team)
        if not vals:
            return self.cfg.default_off_xpts
        return float(vals.get("off_xpts_per_game", self.cfg.default_off_xpts))

    def _get_def_xpts(self, team: str) -> float:
        vals = self.team_xpts.get(team)
        if not vals:
            return self.cfg.default_def_xpts
        return float(vals.get("def_xpts_per_game", self.cfg.default_def_xpts))

    def process(self, context: GameContext):
        """
        Основной метод для pipeline.
        """

        # Ожидаемые очки нападения каждой команды
        off_home = self._get_off_xpts(context.home)
        off_away = self._get_off_xpts(context.away)

        # Ожидаемые очки защиты (сколько допускают)
        def_home = self._get_def_xpts(context.home)
        def_away = self._get_def_xpts(context.away)

        # Разница shot quality в матчапе:
        # нападение home против защиты away и наоборот.
        # Это очень грубый, но полезный показатель.
        matchup_home = off_home - def_away
        matchup_away = off_away - def_home

        shot_quality_delta = (matchup_home - matchup_away) * self.cfg.shot_quality_weight

        context.add_feature("xpts_off_home", off_home)
        context.add_feature("xpts_off_away", off_away)
        context.add_feature("xpts_def_home", def_home)
        context.add_feature("xpts_def_away", def_away)

        context.add_feature("xpts_matchup_home", matchup_home)
        context.add_feature("xpts_matchup_away", matchup_away)
        context.add_feature("shot_quality_delta", shot_quality_delta)
