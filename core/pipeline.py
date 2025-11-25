# core/pipeline.py

from __future__ import annotations
from typing import List

from core.context import GameContext


class GameModelPipeline:
    """
    Универсальный пайплайн обработки одной игры.

    - feature_modules: модули, которые добавляют фичи в GameContext
        (усталость, состав, темп, мотивация, xPTS и т.д.)

    - model_modules: модули, которые считают итоговые модели
        (ожидаемая разница, вероятности, симуляции, value и т.д.)
    """

    def __init__(self, feature_modules: List[object] | None = None,
                 model_modules: List[object] | None = None):
        self.feature_modules = feature_modules or []
        self.model_modules = model_modules or []

    def run_for_game(self, context: GameContext) -> GameContext:
        """
        Запускает все feature-модули, затем все model-модули.
        """

        # 1. Считаем фичи
        for module in self.feature_modules:
            # каждый модуль должен иметь метод .process(context)
            module.process(context)

        # 2. Считаем модельные выводы
        for model in self.model_modules:
            model.process(context)

        return context
