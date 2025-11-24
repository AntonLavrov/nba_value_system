# core/pipeline.py

class GameModelPipeline:
    def __init__(self, feature_modules=None, model_modules=None):
        self.feature_modules = feature_modules or []
        self.model_modules = model_modules or []

    def run_for_game(self, context):
        # 1. Сначала генерируем фичи
        for module in self.feature_modules:
            module.process(context)

        # 2. Потом считаем модели
        for model in self.model_modules:
            model.process(context)

        return context
