from core.pipeline import GameModelPipeline
from core.context import GameContext
from core.features.fatigue import FatigueModule
from core.features.lineup import LineupModule
from core.features.pace import PaceModule
from core.features.motivation import MotivationModule
from core.features.xpts import XPTSModule
from core.model.expected import ExpectedModel
from core.model.probabilities import ProbabilityModel
from core.model.simulation import SimulationModel

def process_game(game):
    context = GameContext(
        game_id=game.id,
        date=game.date,
        home=game.home,
        away=game.away
    )

    pipeline = GameModelPipeline(
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

    context = pipeline.run_for_game(context)
    return context
