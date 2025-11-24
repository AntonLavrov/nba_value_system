# core/model/probabilities.py

from core.context import GameContext
import math

class ProbabilityModel:
    def process(self, context: GameContext):
        expected_diff = context.model_outputs.get("expected_diff", 0.0)

        # преобразование diff в вероятность — адаптируй под свой код
        prob_home_win = 1 / (1 + math.exp(-0.1 * expected_diff))

        context.set_output("win_prob_home", prob_home_win)
        context.set_output("win_prob_away", 1.0 - prob_home_win)
