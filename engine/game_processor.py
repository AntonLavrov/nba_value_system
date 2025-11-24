# engine/game_processor.py

from core.context import GameContext
from core.pipeline import GameModelPipeline

# FEATURES
from core.features.fatigue import FatigueModule
from core.features.lineup import LineupModule
from core.features.pace import PaceModule
from core.features.motivation import MotivationModule
from core.features.xpts import XPTSModule

# MODELS
from core.model.expected import ExpectedModel
from core.model.probabilities import ProbabilityModel
from core.model.simulation import SimulationModel


class GameProcessor:
    """
    Обрабатывает одну игру: создаёт context, запускает pipeline.
    """

    def __init__(self):
        self.pipeline = GameModelPipeline(
            feature_modules=[
                FatigueModule(),
                LineupModule(),
                PaceModule(),
                MotivationModule(),
                XPTSModule()
            ],
            model_modules=[
                ExpectedModel(),
                ProbabilityModel(),
                SimulationModel()
            ]
        )

    def process(self, game):
        """
        game — объект, содержащий:
         - game.id
         - game.date
         - game.home
         - game.away
         - (доп. поля: рейтинги, odds, травмы)
        """

        context = GameContext(
            game_id=game.id,
            date=game.date,
            home=game.home,
            away=game.away
        )

        # Здесь можно передать фичи, которые уже есть в game
        if hasattr(game, "rating_home"):
            context.add_feature("rating_home", game.rating_home)
        if hasattr(game, "rating_away"):
            context.add_feature("rating_away", game.rating_away)

        return self.pipeline.run_for_game(context)
