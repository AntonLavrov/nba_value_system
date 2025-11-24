# core/model/expected.py

from core.context import GameContext


class ExpectedModel:
    def process(self, context: GameContext):
        """
        Интегрированная модель ожидаемого диффа.

        Использует:
        - базовые рейтинги команд (rating_home / rating_away)
        - усталость (fatigue_home / fatigue_away)
        - состав (lineup_home / lineup_away)
        - мотивацию (motivation_home / motivation_away)
        - shot quality (shot_quality_delta)
        - темп (pace_match vs league_avg_pace)
        """

        # ---- базовый дифф по рейтингу ----
        rating_home = context.features.get("rating_home", 0.0)
        rating_away = context.features.get("rating_away", 0.0)
        home_court_adv = context.features.get("home_court_adv", 0.0)

        base_diff = rating_home - rating_away + home_court_adv

        # ---- усталость ----
        fatigue_home = context.features.get("fatigue_home", 0.0)
        fatigue_away = context.features.get("fatigue_away", 0.0)
        fatigue_adj = fatigue_home - fatigue_away

        # ---- состав / травмы ----
        lineup_home = context.features.get("lineup_home", 0.0)
        lineup_away = context.features.get("lineup_away", 0.0)
        lineup_adj = lineup_home - lineup_away

        # ---- мотивация ----
        motivation_home = context.features.get("motivation_home", 0.0)
        motivation_away = context.features.get("motivation_away", 0.0)
        motivation_adj = motivation_home - motivation_away

        # ---- shot quality (xPTS) ----
        shot_quality_delta = context.features.get("shot_quality_delta", 0.0)

        # ---- темп ----
        pace_match = context.features.get("pace_match", 0.0)
        league_avg_pace = context.features.get("league_avg_pace", 0.0)
        pace_factor = 1.0
        if pace_match > 0 and league_avg_pace > 0:
            pace_factor = pace_match / league_avg_pace

        # ---- финальный ожидаемый дифф ----
        expected_diff = base_diff
        expected_diff += fatigue_adj
        expected_diff += lineup_adj
        expected_diff += motivation_adj
        expected_diff += shot_quality_delta

        # мягко учитываем темп (опционально)
        expected_diff *= pace_factor

        context.set_output("expected_diff", expected_diff)
