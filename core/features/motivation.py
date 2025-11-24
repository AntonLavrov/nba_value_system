# core/features/motivation.py

class MotivationModule:
    def process(self, context):
        context.add_feature("motivation_home", 0.0)
        context.add_feature("motivation_away", 0.0)
