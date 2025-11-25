# engine/game_processor.py

from core.context import GameContext
from core.pipeline import GameModelPipeline

# === FEATURES ===
from core.features.fatigue import FatigueModule
from core.features.lineup import LineupModule
from core.features.pace import PaceModule
from core.features.motivation import MotivationModule
from core.features.xpts import XPTSModule

# === MODELS ===
from core.model.expected import ExpectedModel
from core.model.probabilities import ProbabilityModel
from core.model.simulation import SimulationModel
from core.model.value import ValueModel

# === PARSERS ===
from parsers.schedule_parser import load_full_season_schedule


class GameProcessor:
    """
    Обрабатывает одну игру: создаёт GameContext, запускает pipeline.
    """

    def __init__(self):
        # ----------------------
        # F A T I G U E   E N G I N E
        # ----------------------
        self.fatigue = FatigueModule()

        # Загружаем расписание (для усталости)
        schedule = load_full_season_schedule()
        self.fatigue.load_schedule(schedule)

        # ----------------------
        # P I P E L I N E
        # ----------------------
        self.pipeline = GameModelPipeline(
            feature_modules=[
                self.fatigue,         # усталость
                LineupModule(),       # состав / травмы
                PaceModule(),         # темп
                MotivationModule(),   # мотивация
                XPTSModule()          # качество бросков / xPTS
            ],
            model_modules=[
                ExpectedModel(),      # ожидаемый дифф
                ProbabilityModel(),   # вероятность победы
                SimulationModel(),    # Монте-Карло
                ValueModel()          # edge / Kelly (value ставки)
            ]
        )

    # ===================================================================

    def process(self, game):
        """
        Игра → GameContext → полная модель → прогноз.
        """

        # Создаём context
        context = GameContext(
            game_id=game.id,
            date=game.date,
            home=game.home,
            away=game.away
        )

        # --------------------------------------------
        # ДОБАВЛЯЕМ ВСЕ ДАННЫЕ ОТ ПАРСЕРОВ:
        # --------------------------------------------

        # Рейтинги команд
        if hasattr(game, "rating_home"):
            context.add_feature("rating_home", game.rating_home)
        if hasattr(game, "rating_away"):
            context.add_feature("rating_away", game.rating_away)

        # Травмы
        if hasattr(game, "injuries_home"):
            context.add_feature("injuries_home", game.injuries_home)
        else:
            context.add_feature("injuries_home", [])

        if hasattr(game, "injuries_away"):
            context.add_feature("injuries_away", game.injuries_away)
        else:
            context.add_feature("injuries_away", [])

        # Коэффициенты на матч
        if hasattr(game, "odds") and isinstance(game.odds, dict):
            odds_home = game.odds.get("home")
            odds_away = game.odds.get("away")
            if odds_home is not None:
                context.add_feature("odds_home", float(odds_home))
            if odds_away is not None:
                context.add_feature("odds_away", float(odds_away))

        # Домашний фактор (можно вынести в config)
        context.add_feature("home_court_adv", 2.5)

        # --------------------------------------------
        # ЗАПУСК ПАЙПЛАЙНА
        # --------------------------------------------
        context = self.pipeline.run_for_game(context)
        return context
