from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math

from core.context import GameContext


@dataclass
class ExpectedConfig:
    """
    Настройки расчёта ожидаемого разницы очков (home − away).
    Все коэффициенты подобраны так, чтобы их можно было калибровать на истории.
    """
    rating_scale: float = 1.0
    fatigue_weight: float = 1.0
    lineup_weight: float = 1.0
    motivation_weight: float = 1.0
    shot_quality_weight: float = 1.0
    pace_weight: float = 1.0

    elo_point_scale: float = 400.0     # «шкала» Elo
    base_point_spread: float = 12.0    # сколько очков соответствует 400 Elo


class ExpectedModel:
    """
    Продвинутая модель ожидаемого дифференциала.
    Использует:
      Elo-подобное преобразование рейтингов,
      усталость,
      состав,
      мотивацию,
      shot quality (xPTS),
      темп.
    """

    def __init__(self, config: Optional[ExpectedConfig] = None):
        self.cfg = config or ExpectedConfig()

    def process(self, context: GameContext):
        # ---------- БАЗОВЫЕ РЕЙТИНГИ ----------
        rating_home = context.features.get("rating_home", 0.0)
        rating_away = context.features.get("rating_away", 0.0)
        home_court = context.features.get("home_court_adv", 0.0)

        rating_diff = rating_home - rating_away

        # Elo → дифф очков
        if self.cfg.elo_point_scale > 0:
            p_home_elo = 1.0 / (1.0 + math.pow(10.0, -(rating_diff) / self.cfg.elo_point_scale))
            elo_diff = (p_home_elo - 0.5) * 2.0 * self.cfg.base_point_spread
        else:
            elo_diff = rating_diff

        base_diff = elo_diff * self.cfg.rating_scale + home_court

        # ---------- УСТАЛОСТЬ ----------
        fatigue_home = context.features.get("fatigue_home", 0.0)
        fatigue_away = context.features.get("fatigue_away", 0.0)
        fatigue_adj = (fatigue_home - fatigue_away) * self.cfg.fatigue_weight

        # ---------- СОСТАВ ----------
        lineup_home = context.features.get("lineup_home", 0.0)
        lineup_away = context.features.get("lineup_away", 0.0)
        lineup_adj = (lineup_home - lineup_away) * self.cfg.lineup_weight

        # ---------- МОТИВАЦИЯ ----------
        motivation_home = context.features.get("motivation_home", 0.0)
        motivation_away = context.features.get("motivation_away", 0.0)
        motivation_adj = (motivation_home - motivation_away) * self.cfg.motivation_weight

        # ---------- xPTS / SHOT QUALITY ----------
        shot_quality_delta = context.features.get("shot_quality_delta", 0.0)
        shot_quality_adj = shot_quality_delta * self.cfg.shot_quality_weight

        # ---------- ТЕМП ----------
        pace_match = context.features.get("pace_match", 100.0)
        league_pace = context.features.get("league_avg_pace", 100.0)

        if league_pace > 0:
            relative_pace = pace_match / league_pace
            pace_factor = 1.0 + (relative_pace - 1.0) * self.cfg.pace_weight
        else:
            pace_factor = 1.0

        # ---------- ФИНАЛЬНЫЙ EXPECTED DIFF ----------
        expected_diff = (
            base_diff
            + fatigue_adj
            + lineup_adj
            + motivation_adj
            + shot_quality_adj
        )

        expected_diff *= pace_factor

        context.set_output("expected_diff", expected_diff)
