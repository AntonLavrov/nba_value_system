# core/export/export_xlsx.py

from openpyxl import Workbook
from core.export.labels_ru import COLUMN_LABELS_RU


def _excel_safe(value):
    """
    Excel не принимает списки и сложные структуры.
    Преобразуем:
      - списки -> строка "a, b, c"
      - None -> ""
      - другие типы оставляем как есть
    """
    if value is None:
        return ""
    if isinstance(value, list):
        if len(value) == 0:
            return "-"
        # конвертируем список в строку
        return ", ".join(str(v) for v in value)
    return value


def export_to_xlsx(contexts, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "NBA Модель"

    # -----------------------------------------
    # Список всех колонок
    # -----------------------------------------
    columns = [
        "game_id", "date", "home", "away",
    ]

    dynamic_keys = set()
    for ctx in contexts:
        dynamic_keys.update(ctx.features.keys())
        dynamic_keys.update(ctx.model_outputs.keys())

    columns.extend(sorted(dynamic_keys))

    # -----------------------------------------
    # Заголовки (русские)
    # -----------------------------------------
    header = []
    for col in columns:
        header.append(COLUMN_LABELS_RU.get(col, col))
    ws.append(header)

    # -----------------------------------------
    # Строки данных
    # -----------------------------------------
    for ctx in contexts:
        row = []
        for col in columns:
            if col == "game_id":
                val = ctx.game_id
            elif col == "date":
                val = str(ctx.date)
            elif col == "home":
                val = ctx.home
            elif col == "away":
                val = ctx.away
            else:
                if col in ctx.features:
                    val = ctx.features[col]
                else:
                    val = ctx.model_outputs.get(col)

            # Делаем значение "Excel-безопасным"
            val = _excel_safe(val)
            row.append(val)

        ws.append(row)

    wb.save(path)
