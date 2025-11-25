# core/context.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import date


@dataclass
class GameContext:
    """
    Универсальный контейнер данных по матчу.

    - features: все рассчитанные фичи (усталость, мотивация и т.д.)
    - model_outputs: результаты всех моделей (expected_diff, win probability, sim results...)
    """

    game_id: str
    date: date
    home: str
    away: str

    # Здесь хранятся фичи, которые собирают feature-модули
    features: Dict[str, Any] = field(default_factory=dict)

    # Результаты моделей (ExpectedModel, SimulationModel, ValueModel)
    model_outputs: Dict[str, Any] = field(default_factory=dict)

    # -----------------------------------------------------------
    # Методы добавления
    # -----------------------------------------------------------

    def add_feature(self, key: str, value: Any):
        """Добавляет фичу (промежуточное значение)."""
        self.features[key] = value

    def set_output(self, key: str, value: Any):
        """Сохраняет результаты модели."""
        self.model_outputs[key] = value

    # -----------------------------------------------------------
    # Удобные методы доступа
    # -----------------------------------------------------------

    def get(self, key: str):
        if key in self.features:
            return self.features[key]
        if key in self.model_outputs:
            return self.model_outputs[key]
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Полный экспорт объекта."""
        base = {
            "game_id": self.game_id,
            "date": str(self.date),
            "home": self.home,
            "away": self.away,
        }
        combined = {**base, **self.features, **self.model_outputs}
        return combined
