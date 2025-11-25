# core/export/export_xlsx.py

from openpyxl import Workbook
from core.export.labels_ru import COLUMN_LABELS_RU


def export_to_xlsx(contexts, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "NBA Модель"

    # -----------------------------------------
    # Список всех возможных колонок
    # -----------------------------------------
    columns = [
        "game_id", "date", "home", "away",
    ]

    # добавляем динамические ключи
    dynamic_keys = set()
    for ctx in contexts:
        dynamic_keys.update(ctx.features.keys())
        dynamic_keys.update(ctx.model_outputs.keys())

    columns.extend(sorted(dynamic_keys))

    # -----------------------------------------
    # Заголовки (по-русски)
    # -----------------------------------------
    header = []
    for col in columns:
        header.append(COLUMN_LABELS_RU.get(col, col))
    ws.append(header)

    # -----------------------------------------
    # Данные
    # -----------------------------------------
    for ctx in contexts:
        row = []
        for col in columns:
            val = (
                ctx.features.get(col)
                if col in ctx.features
                else ctx.model_outputs.get(col)
            )
            # базовая информация
            if col == "game_id":
                val = ctx.game_id
            if col == "date":
                val = str(ctx.date)
            if col == "home":
                val = ctx.home
            if col == "away":
                val = ctx.away

            row.append(val)
        ws.append(row)

    wb.save(path)
