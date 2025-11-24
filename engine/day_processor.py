# engine/day_processor.py

from engine.game_processor import GameProcessor

class DayProcessor:
    def __init__(self):
        self.game_processor = GameProcessor()

    def process_day(self, games):
        """
        games — список игровых объектов.
        Возвращает список контекстов (GameContext).
        """
        results = []
        for game in games:
            context = self.game_processor.process(game)
            results.append(context)
        return results
