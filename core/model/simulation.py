# core/model/simulation.py

from __future__ import annotations
import random
import math
from dataclasses import dataclass

from core.context import GameContext


@dataclass
class SimulationConfig:
    num_simulations: int = 5000   # Количество симуляций
    score_std: float = 12.0       # Стандартное отклонение счёта команды
    pace_factor_weight: float = 0.5  # Насколько темп влияет на variance
    xpts_weight: float = 0.3         # Насколько shot-quality влияет на variance


class SimulationModel:
    """
    Monte-Carlo модель для симуляции результата матча.
    """

    def __init__(self, config: SimulationConfig | None = None):
        self.cfg = config or SimulationConfig()

    # ---------------------------------------------------------------------

    def _sample_team_score(self, mean_score: float, variance_factor: float) -> int:
        """
        Генерирует очки команды по нормальному распределению.
        """

        sd = self.cfg.score_std * variance_factor
        score = random.gauss(mean_score, sd)
        return max(60, int(score))  # минимальная граница для NBA

    # ---------------------------------------------------------------------

    def process(self, context: GameContext):

        expected_diff = context.model_outputs.get("expected_diff", 0.0)

        # Достаём основные фичи
        pace = context.features.get("pace_match", 100.0)
        league_pace = context.features.get("league_avg_pace", 100.0)

        # Shot quality
        xpts_home = context.features.get("xpts_off_home", 112.0)
        xpts_away = context.features.get("xpts_off_away", 112.0)

        # ------------------------------------------------------------------
        #  Строим базовые ожидаемые очки команд на игру
        # ------------------------------------------------------------------
        mean_home_score = max(80, (xpts_home + expected_diff / 2))
        mean_away_score = max(80, (xpts_away - expected_diff / 2))

        # ------------------------------------------------------------------
        #  Variance: темп влияет на разброс
        # ------------------------------------------------------------------

        pace_factor = ((pace / league_pace) ** self.cfg.pace_factor_weight)

        # Shot quality также влияет на variance: команды с высоким xPTS
        # играют более нестабильно — больше трехочковых, подборов, транзишна.
        xpts_factor = (
            (abs(xpts_home - xpts_away) / 10) ** self.cfg.xpts_weight
        )

        variance_factor = max(0.8, min(2.0, pace_factor + xpts_factor))

        # ------------------------------------------------------------------
        #  Monte Carlo Simulation
        # ------------------------------------------------------------------

        home_wins = 0
        away_wins = 0

        diff_distribution = []
        total_distribution = []

        for _ in range(self.cfg.num_simulations):

            score_home = self._sample_team_score(mean_home_score, variance_factor)
            score_away = self._sample_team_score(mean_away_score, variance_factor)

            diff = score_home - score_away
            total = score_home + score_away

            diff_distribution.append(diff)
            total_distribution.append(total)

            if diff > 0:
                home_wins += 1
            else:
                away_wins += 1

        # Вероятности
        win_prob_home = home_wins / self.cfg.num_simulations
        win_prob_away = away_wins / self.cfg.num_simulations

        # ------------------------------------------------------------------
        #  Записываем в context
        # ------------------------------------------------------------------
        context.set_output("mc_win_prob_home", win_prob_home)
        context.set_output("mc_win_prob_away", win_prob_away)

        context.set_output("mc_diff_distribution", diff_distribution)
        context.set_output("mc_total_distribution", total_distribution)

        # Можно также сохранить:
        context.set_output("mc_expected_total", sum(total_distribution) / len(total_distribution))
        context.set_output("mc_expected_diff", sum(diff_distribution) / len(diff_distribution))
