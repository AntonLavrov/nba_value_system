# core/model/simulation.py

from core.context import GameContext

class SimulationModel:
    def process(self, context: GameContext):
        # Пока что просто передаём вероятность из ProbabilityModel
        mc_win_prob_home = context.model_outputs.get("win_prob_home", 0.0)
        mc_win_prob_away = context.model_outputs.get("win_prob_away", 0.0)

        context.set_output("mc_win_prob_home", mc_win_prob_home)
        context.set_output("mc_win_prob_away", mc_win_prob_away)
