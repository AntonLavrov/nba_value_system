# core/context.py
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Any


@dataclass
class GameContext:
    game_id: str
    date: date
    home: str
    away: str

    # Фичи от модулей (fatigue, pace, lineup…)
    features: Dict[str, Any] = field(default_factory=dict)

    # Входы модели (expected_diff_input, possessions, xpts…)
    model_inputs: Dict[str, float] = field(default_factory=dict)

    # Выходы модели (expected_diff, win_prob, value…)
    model_outputs: Dict[str, Any] = field(default_factory=dict)

    def add_feature(self, name: str, value: Any):
        self.features[name] = value

    def set_input(self, name: str, value: float):
        self.model_inputs[name] = value

    def set_output(self, name: str, value: Any):
        self.model_outputs[name] = value
