from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math

from core.context import GameContext


@dataclass
class ProbabilityConfig:
    """
    Настройки логистической модели.
    - base_logistic_scale: базовый наклон логистики
    - diff_std_ref: референсное StdDeviation для калибровки
    - blend_mc_weight: 0–1, насколько сильно доверяем Монте-Карло
    """
    base_logistic_scale: float = 0.12
    diff_std_ref: float = 12.0
    blend_mc_weight: float = 0.5


class ProbabilityModel:
    def __init__(self, config: Optional[ProbabilityConfig] = None):
        self.cfg = config or ProbabilityConfig()

    def _logistic(self, diff: float, scale: float) -> float:
        return 1.0 / (1.0 + math.exp(-scale * diff))

    def process(self, context: GameContext):
        expected_diff = context.model_outputs.get("expected_diff", 0.0)

        # -----------------------------
        #   Дисперсия по Монте-Карло
        # -----------------------------
        mc_diffs = context.model_outputs.get("mc_diff_distribution")
        diff_std = None
        if isinstance(mc_diffs, (list, tuple)) and mc_diffs:
            m = sum(mc_diffs) / len(mc_diffs)
            var = sum((x - m) ** 2 for x in mc_diffs) / len(mc_diffs)
            diff_std = math.sqrt(max(var, 1e-6))

        # -----------------------------
        #   Калибруем наклон логистики
        # -----------------------------
        scale = self.cfg.base_logistic_scale
        if diff_std and diff_std > 0:
            scale = self.cfg.base_logistic_scale * (self.cfg.diff_std_ref / diff_std)

        p_logistic = self._logistic(expected_diff, scale)

        # -----------------------------
        #   Смешиваем с MC
        # -----------------------------
        mc_prob_home = context.model_outputs.get("mc_win_prob_home")

        if isinstance(mc_prob_home, (int, float)):
            alpha = self.cfg.blend_mc_weight
            p_home = alpha * mc_prob_home + (1 - alpha) * p_logistic
        else:
            p_home = p_logistic

        p_home = max(0.0, min(1.0, p_home))
        p_away = 1.0 - p_home

        # -----------------------------
        #   Сохраняем
        # -----------------------------
        context.set_output("win_prob_home_logistic", p_logistic)
        context.set_output("win_prob_home", p_home)
        context.set_output("win_prob_away", p_away)

        if diff_std:
            context.set_output("diff_std_estimate", diff_std)
        if mc_prob_home is not None:
            context.set_output("mc_vs_model_gap", p_home - mc_prob_home)
