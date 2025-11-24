# core/features/xpts.py

class XPTSModule:
    def process(self, context):
        context.add_feature("xpts_home", 110.0)
        context.add_feature("xpts_away", 108.0)
