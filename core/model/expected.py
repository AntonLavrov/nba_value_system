# core/model/expected.py

from core.context import GameContext

class ExpectedModel:
    def process(self, context: GameContext):
        """
        Перенесена логика из model_ev.py и model_expectations.py
        """

        # пример: базовая оценка команды
        rating_home = context.features.get("rating_home", 0.0)
        rating_away = context.features.get("rating_away", 0.0)
        home_court_adv = context.features.get("home_court_adv", 0.0)

        base_diff = rating_home - rating_away + home_court_adv

        # учёт усталости
        fatigue_home = context.features.get("fatigue_home", 0.0)
        fatigue_away = context.features.get("fatigue_away", 0.0)
        fatigue_adj = fatigue_home - fatigue_away

        # учёт состава
        lineup_home = context.features.get("lineup_home", 0.0)
        lineup_away = context.features.get("lineup_away", 0.0)
        lineup_adj = lineup_home - lineup_away

        # учёт мотивации
        motivation_home = context.features.get("motivation_home", 0.0)
        motivation_away = context.features.get("motivation_away", 0.0)
        motivation_adj = motivation_home - motivation_away

        # учёт темпа (может влиять на дифф)
        pace = context.features.get("pace", 0.0)

        expected_diff = base_diff + fatigue_adj + lineup_adj + motivation_adj

        # если хочешь, темп корректирует коэффициент
        if pace:
            expected_diff *= (pace / 100.0)

        context.set_output("expected_diff", expected_diff)
