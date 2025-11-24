# core/model/expected.py

from core.context import GameContext

class ExpectedModel:
    def process(self, context: GameContext):

        # Базовый рейтинг (это твой код перенесем внутрь)
        rating_base = (
            context.features.get("rating_home", 0)
            - context.features.get("rating_away", 0)
        )

        # Усталость
        fatigue_adj = (
            context.features.get("fatigue_home", 0)
            - context.features.get("fatigue_away", 0)
        )

        expected_diff = rating_base + fatigue_adj

        context.set_output("expected_diff", expected_diff)
