# core/export/export_json.py

import json

def export_to_json_flat(contexts, path):
    """
    Экспортирует список контекстов матчей в плоский JSON для фронтенда.
    Каждый контекст должен иметь метод to_flat_dict().
    """
    flat = []
    for ctx in contexts:
        if hasattr(ctx, "to_flat_dict"):
            flat.append(ctx.to_flat_dict())
        else:
            # fallback — если почему-то нет метода
            base = {
                "game_id": ctx.game_id,
                "date": str(ctx.date),
                "home": ctx.home,
                "away": ctx.away,
            }
            if hasattr(ctx, "features"):
                base.update(ctx.features)
            if hasattr(ctx, "model_outputs"):
                base.update(ctx.model_outputs)
            flat.append(base)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)
