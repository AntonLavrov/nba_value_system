# data/game_object.py

class Game:
    def __init__(self, id, date, home, away):
        self.id = id
        self.date = date
        self.home = home
        self.away = away

        # дополнительные поля (добавятся позже)
        self.rating_home = None
        self.rating_away = None
        self.injuries_home = []
        self.injuries_away = []
        self.odds = {}
