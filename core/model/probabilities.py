# core/model/probabilities.py

from core.context import GameContext
import math

class ProbabilityModel:
    def process(self, context: GameContext):

        diff = context.model_outputs.get("expected_diff", 0)

        # логистическая вероятность (пример, но мы сюда перенесём твой код)
        win_prob = 1 / (1 + math.exp(-0.1 * diff))

        context.set_output("win_prob", win_prob)
