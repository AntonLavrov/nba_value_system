# core/export/export_json.py

import json


def export_to_json(contexts, path):
    """
    Экспортирует результаты в JSON.
    """

    out = []

    for ctx in contexts:
        row = {
            "game_id": ctx.game_id,
            "date": str(ctx.date),
            "home": ctx.home,
            "away": ctx.away,
        }

        # фичи
        row.update(ctx.features)

        # результаты моделей
        row.update(ctx.model_outputs)

        out.append(row)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=4)
