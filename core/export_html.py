import json
import os
import pandas as pd

INPUT_JSON = "outputs/value_today.json"
OUTPUT_HTML = "outputs/value_today.html"


def main():
    # 1. Загружаем результаты модели
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        results = json.load(f)

    rows = []

    for game in results:
        home = game.get("home")
        away = game.get("away")
        matchup = f"{home} – {away}"

        for v in game.get("value_lines", []):
            price = float(v["price"])
            p_model = float(v["model_prob"])
            ev = float(v["ev"])

            # честный кэф по модели
            fair_odds = 1.0 / p_model if p_model > 0 else None

            # вероятность букмекера
            implied_prob = 1.0 / price if price > 0 else None

            # перекос (edge) в процентах
            edge_pct = None
            if implied_prob is not None:
                edge_pct = (p_model - implied_prob) * 100.0

            rows.append({
                "Матч": matchup,
                "Дом": home,
                "Гости": away,
                "Рынок": v.get("market", ""),
                "Сторона": v.get("side", v.get("team", "")),
                "Линия": v.get("line", ""),
                "Коэфф. букмекера": round(price, 3),
                "P модели": round(p_model, 4),
                "Честный кэф": round(fair_odds, 3) if fair_odds else "",
                "P букмекера": round(implied_prob, 4) if implied_prob else "",
                "Перекос, %": round(edge_pct, 1) if edge_pct is not None else "",
                "EV": round(ev, 3),
            })

    if not rows:
        print("Нет данных для экспорта в HTML.")
        return

    df = pd.DataFrame(rows)

    # сортируем по EV (самые жирные сверху)
    df = df.sort_values("EV", ascending=False).reset_index(drop=True)

    # генерируем HTML-таблицу
    html_table = df.to_html(index=False, classes="value-table", border=0)

    # оборачиваем в красивый шаблон
    template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>NBA value-ставки</title>
<style>
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background:#020617;
  color:#e5e7eb;
  padding:24px;
}}
h1 {{
  font-size:24px;
  margin-bottom:8px;
}}
h2 {{
  font-size:16px;
  margin-bottom:16px;
  color:#9ca3af;
  font-weight:400;
}}
.table-wrapper {{
  overflow-x:auto;
  background:#020617;
  padding:16px;
  border-radius:12px;
  box-shadow:0 20px 40px rgba(0,0,0,.6);
  border:1px solid #1f2937;
}}
.value-table {{
  border-collapse:collapse;
  width:100%;
  font-size:13px;
}}
.value-table thead tr {{
  background:#0f172a;
}}
.value-table th, .value-table td {{
  padding:6px 10px;
  border-bottom:1px solid #1f2937;
  text-align:center;
  white-space:nowrap;
}}
.value-table tbody tr:nth-child(odd) td {{
  background:#020617;
}}
.value-table tbody tr:nth-child(even) td {{
  background:#020617;
}}
.value-table tbody tr:hover td {{
  background:#111827;
}}
.positive-ev {{
  color:#4ade80;
  font-weight:600;
}}
.negative-ev {{
  color:#f87171;
}}
.neutral-ev {{
  color:#e5e7eb;
}}
.bad-edge {{
  opacity:0.55;
}}
</style>
</head>
<body>
  <h1>NBA value-ставки (модель)</h1>
  <h2>Отчёт по всем матчам дня. Отсортировано по EV (сверху самые выгодные по модели).</h2>
  <div class="table-wrapper">
    {html_table}
  </div>
<script>
// Подсветка EV и срез "мусорных" ставок
document.addEventListener('DOMContentLoaded', () => {{
  const rows = document.querySelectorAll('.value-table tbody tr');
  rows.forEach(row => {{
    const evCell = row.cells[row.cells.length - 1];
    const edgeCell = row.cells[row.cells.length - 2];

    if (!evCell) return;
    const ev = parseFloat(evCell.textContent.replace(',', '.'));
    if (isNaN(ev)) return;

    if (ev > 0.10) evCell.classList.add('positive-ev');
    else if (ev < 0) evCell.classList.add('negative-ev');
    else evCell.classList.add('neutral-ev');

    if (edgeCell) {{
      const edge = parseFloat(edgeCell.textContent.replace(',', '.'));
      if (!isNaN(edge) && edge < 0) {{
        row.classList.add('bad-edge');
      }}
    }}
  }});
}});
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"HTML отчёт сохранён: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
