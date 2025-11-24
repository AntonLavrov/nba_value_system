# core/features/lineup.py

class LineupModule:
    def process(self, context):
        context.add_feature("lineup_home", 0.0)
        context.add_feature("lineup_away", 0.0)
