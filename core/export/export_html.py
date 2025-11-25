# core/export/export_html.py

from core.export.labels_ru import COLUMN_LABELS_RU


def export_to_html(contexts, path):
    columns = [
        "game_id", "date", "home", "away",
    ]

    dynamic_keys = set()
    for ctx in contexts:
        dynamic_keys.update(ctx.features.keys())
        dynamic_keys.update(ctx.model_outputs.keys())

    columns.extend(sorted(dynamic_keys))

    # -----------------------------------------
    # HTML
    # -----------------------------------------
    html = []
    html.append("<html><head><meta charset='utf-8'><title>NBA Модель</title>")
    html.append("""
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid gray; padding: 4px 8px; }
        th { background: #eee; }
    </style>
    """)
    html.append("</head><body>")
    html.append("<h1>Результаты модели NBA</h1>")
    html.append("<table>")
    html.append("<tr>")

    # заголовки
    for col in columns:
        name = COLUMN_LABELS_RU.get(col, col)
        html.append(f"<th>{name}</th>")
    html.append("</tr>")

    # данные
    for ctx in contexts:
        html.append("<tr>")
        for col in columns:
            val = (
                ctx.features.get(col)
                if col in ctx.features
                else ctx.model_outputs.get(col)
            )
            if col == "game_id":
                val = ctx.game_id
            if col == "date":
                val = str(ctx.date)
            if col == "home":
                val = ctx.home
            if col == "away":
                val = ctx.away

            html.append(f"<td>{val}</td>")
        html.append("</tr>")
    html.append("</table></body></html>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
