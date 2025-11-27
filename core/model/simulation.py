from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List

from core.context import GameContext


@dataclass
class SimulationConfig:
    num_simulations: int = 5000   # Количество симов
    score_std: float = 12.0       # Базовая дисперсия очков
    pace_factor_weight: float = 0.5
    xpts_weight: float = 0.3


class SimulationModel:
    """
    Monte Carlo симуляция для счета:
      - home_pts
      - away_pts
      - total
      - diff
    Учитывает:
      expected_diff,
      xPTS,
      темп,
      variance_factor.
    """

    def __init__(self, config: SimulationConfig | None = None):
        self.cfg = config or SimulationConfig()

    def _sample_team_score(self, mean_score: float, variance_factor: float) -> int:
        sd = self.cfg.score_std * variance_factor
        val = random.gauss(mean_score, sd)
        return max(60, int(round(val)))

    def process(self, context: GameContext):
        expected_diff = context.model_outputs.get("expected_diff", 0.0)

        # -------- xPTS (качество атаки) ----------
        xpts_home = context.features.get("xpts_off_home", 112.0)
        xpts_away = context.features.get("xpts_off_away", 112.0)

        # --- Базовое ожидание очков команд ---
        mean_home = max(80, xpts_home + expected_diff / 2)
        mean_away = max(80, xpts_away - expected_diff / 2)

        # -------- ТЕМП / VARIANCE ----------
        pace = context.features.get("pace_match", 100.0)
        league_pace = context.features.get("league_avg_pace", 100.0)

        if league_pace > 0:
            pace_factor = (pace / league_pace) ** self.cfg.pace_factor_weight
        else:
            pace_factor = 1.0

        xpts_diff = abs(xpts_home - xpts_away)
        xpts_factor = (xpts_diff / 10.0) ** self.cfg.xpts_weight

        variance_factor = max(0.8, min(2.0, pace_factor + xpts_factor))

        # --------- ГОТОВИМ РАСПРЕДЕЛЕНИЯ ----------
        total_distribution: List[int] = []
        diff_distribution: List[int] = []
        home_pts_dist: List[int] = []
        away_pts_dist: List[int] = []

        home_wins = 0
        away_wins = 0

        # ---------- SIMULATIONS -----------
        for _ in range(self.cfg.num_simulations):
            h = self._sample_team_score(mean_home, variance_factor)
            a = self._sample_team_score(mean_away, variance_factor)

            diff = h - a
            total = h + a

            home_pts_dist.append(h)
            away_pts_dist.append(a)
            diff_distribution.append(diff)
            total_distribution.append(total)

            if diff > 0:
                home_wins += 1
            elif diff < 0:
                away_wins += 1
            else:
                home_wins += 0.5
                away_wins += 0.5

        n = float(self.cfg.num_simulations)

        # ---------- ЗАПИСЫВАЕМ В CONTEXT -----------
        context.set_output("mc_win_prob_home", home_wins / n)
        context.set_output("mc_win_prob_away", away_wins / n)

        context.set_output("mc_diff_distribution", diff_distribution)
        context.set_output("mc_total_distribution", total_distribution)
        context.set_output("mc_home_pts_distribution", home_pts_dist)
        context.set_output("mc_away_pts_distribution", away_pts_dist)

        context.set_output("mc_expected_home_pts", sum(home_pts_dist) / n)
        context.set_output("mc_expected_away_pts", sum(away_pts_dist) / n)
        context.set_output("mc_expected_total", sum(total_distribution) / n)
        context.set_output("mc_expected_diff", sum(diff_distribution) / n)
