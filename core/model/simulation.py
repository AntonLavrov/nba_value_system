# core/model/simulation.py

from core.context import GameContext

class SimulationModel:
    def process(self, context: GameContext):
        # Placeholder — позже поставим настоящий симулятор
        context.set_output("mc_win_prob", context.model_outputs.get("win_prob"))
