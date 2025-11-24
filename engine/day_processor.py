from parsers.schedule_parser import load_full_season_schedule
from core.features.fatigue import FatigueModule

class GameProcessor:
    def __init__(self):
        self.fatigue = FatigueModule()

        # загружаем расписание
        schedule = load_full_season_schedule()
        self.fatigue.load_schedule(schedule)

        self.pipeline = GameModelPipeline(
            feature_modules=[
                self.fatigue,
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
