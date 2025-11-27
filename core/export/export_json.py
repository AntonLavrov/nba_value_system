# core/export/export_json.py

import json
from datetime import date, datetime


def _serialize_scalar(value):
    """
    Приведение значений к JSON-дружелюбному виду.
    Даты -> строки. Остальное отдаем как есть.
    """
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _ctx_to_flat_dict(ctx):
    """
    Универсальное преобразование контекста матча к плоскому dict.
    Работает как с объектами, так и с dict-ами.
    Ожидается, что у ctx (если это объект) есть:
      - game_id
      - date
      - home
      - away
      - features (dict)
      - model_outputs (dict)
    """
    # Если это уже dict — аккуратно "распрямляем" features и model_outputs
    if isinstance(ctx, dict):
        base = {}
        # базовые ключи, если есть
        for key in ("game_id", "date", "home", "away"):
            if key in ctx:
                base[key] = _serialize_scalar(ctx[key])

        # features и model_outputs расплющиваем
        features = ctx.get("features", {}) or {}
        model_outputs = ctx.get("model_outputs", {}) or {}

        if isinstance(features, dict):
            for k, v in features.items():
                base[k] = _serialize_scalar(v)

        if isinstance(model_outputs, dict):
            for k, v in model_outputs.items():
                base[k] = _serialize_scalar(v)

        # если вдруг в dict были еще какие-то верхнеуровневые ключи — добавляем их
        for k, v in ctx.items():
            if k in ("game_id", "date", "home", "away", "features", "model_outputs"):
                continue
            if k not in base:
                base[k] = _serialize_scalar(v)

        return base

    # Если это объект-контекст
    base = {}

    # базовые поля
    game_id = getattr(ctx, "game_id", None)
    date_val = getattr(ctx, "date", None)
    home = getattr(ctx, "home", None)
    away = getattr(ctx, "away", None)

    if game_id is not None:
        base["game_id"] = _serialize_scalar(game_id)
    if date_val is not None:
        base["date"] = _serialize_scalar(date_val)
    if home is not None:
        base["home"] = _serialize_scalar(home)
    if away is not None:
        base["away"] = _serialize_scalar(away)

    # features
    features = getattr(ctx, "features", {}) or {}
    if isinstance(features, dict):
        for k, v in features.items():
            base[k] = _serialize_scalar(v)

    # model_outputs
    model_outputs = getattr(ctx, "model_outputs", {}) or {}
    if isinstance(model_outputs, dict):
        for k, v in model_outputs.items():
            base[k] = _serialize_scalar(v)

    return base


def export_to_json_flat(contexts, path):
    """
    Плоский JSON для фронтенда.
    На выходе: список объектов с полями:
      game_id, date, home, away, <все features>, <все model_outputs>
    """
    flat_list = []
    for ctx in contexts:
        flat = _ctx_to_flat_dict(ctx)
        flat_list.append(flat)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(flat_list, f, ensure_ascii=False, indent=2)


def export_to_json(contexts, path):
    """
    Обертка для обратной совместимости.
    Сейчас просто вызывает плоский экспорт.
    """
    export_to_json_flat(contexts, path)
