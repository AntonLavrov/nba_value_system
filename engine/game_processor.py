from __future__ import annotations

from core.context import GameContext
from core.pipeline import GameModelPipeline
from core.features.fatigue import FatigueModule
from core.features.lineup import LineupModule
from core.features.pace import PaceModule
from core.features.motivation import MotivationModule
from core.features.xpts import XPTSModule

from core.model.expected import ExpectedModel
from core.model.simulation import SimulationModel
from core.model.probabilities import ProbabilityModel
from core.model.value import ValueModel


class GameProcessor:
    """
    Создаёт GameContext, добавляет фичи вручную (из объекта Game),
    запускает feature-модули и модельные модули.
    """

    def __init__(self):
        self.fatigue = FatigueModule()

        self.pipeline = GameModelPipeline(
            feature_modules=[
                self.fatigue,
                LineupModule(),
                PaceModule(),
                MotivationModule(),
                XPTSModule(),
            ],
            model_modules=[
                ExpectedModel(),
                SimulationModel(),
                ProbabilityModel(),
                ValueModel(),
            ]
        )

    # -------------------------------------------------------

    def process(self, game):
        """
        game — объект класса Game (data/game_object.py)
        """

        context = GameContext(
            game_id=game.id,
            date=game.date,
            home=game.home,
            away=game.away
        )

        # ---------------------------
        #     Базовые фичи из Game
        # ---------------------------
        if game.rating_home is not None:
            context.add_feature("rating_home", float(game.rating_home))
        if game.rating_away is not None:
            context.add_feature("rating_away", float(game.rating_away))

        context.add_feature("injuries_home", game.injuries_home)
        context.add_feature("injuries_away", game.injuries_away)

        # ---------------------------
        #     ODDS / Lines
        # ---------------------------
        if hasattr(game, "odds") and isinstance(game.odds, dict):
            odds = game.odds

            # Moneyline
            if "home" in odds:
                context.add_feature("odds_home", float(odds["home"]))
            if "away" in odds:
                context.add_feature("odds_away", float(odds["away"]))

            # Spread
            for key in ("spread_line", "spread_odds_home", "spread_odds_away"):
                if key in odds:
                    context.add_feature(key, float(odds[key]))

            # Total
            for key in ("total_line", "total_over_odds", "total_under_odds"):
                if key in odds:
                    context.add_feature(key, float(odds[key]))

            # Team totals
            for key in (
                "home_team_total",
                "home_team_total_over_odds",
                "home_team_total_under_odds",
                "away_team_total",
                "away_team_total_over_odds",
                "away_team_total_under_odds",
            ):
                if key in odds:
                    context.add_feature(key, float(odds[key]))

        # ---------------------------
        #   Запуск PIPELINE
        # ---------------------------
        return self.pipeline.run_for_game(context)
