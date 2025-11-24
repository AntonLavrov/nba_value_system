import os
import json
import pandas as pd


def export_to_json(results, filename: str):
    """
    Просто сохраняем сырые результаты модели (как есть) в JSON.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"JSON сохранён: {filename}")


def export_to_excel(results, filename: str):
    """
    Делаем плоскую таблицу всех value-линий по всем матчам
    и добавляем расчётные поля:
    - честный кэф (1 / p_model)
    - имплицитная вероятность (1 / кэф букмекера)
    - перекос, %
    - риск-скор
    - ранг по EV
    Все названия колонок — на русском.
    """

    rows = []

    for game in results:
        home = game.get("home")
        away = game.get("away")
        matchup = f"{home} – {away}"

        for v in game.get("value_lines", []):
            price = float(v["price"])
            p_model = float(v["model_prob"])
            ev = float(v["ev"])

            # Честный кэф по модели
            fair_odds = 1.0 / p_model if p_model > 0 else None

            # Имплицитная вероятность по кэфу букмекера
            implied_prob = 1.0 / price if price > 0 else None

            # Перекос модели относительно букмекера (в процентах)
            edge = None
            edge_pct = None
            if implied_prob is not None:
                edge = p_model - implied_prob
                edge_pct = edge * 100.0

            # Простой риск-скор:
            # чем больше вероятность И перекос, тем выше "сила" ставки
            risk_score = 0.0
            if edge is not None and edge > 0:
                # можно играть формулой как угодно, это базовый вариант
                risk_score = p_model * edge_pct  # условная метрика

            rows.append({
                "Матч": matchup,
                "Домашняя команда": home,
                "Гостевая команда": away,

                "Тип рынка": v.get("market", ""),          # "победа", "фора", "тотал"
                "Сторона": v.get("side", v.get("team", "")),  # Over/Under или команда
                "Команда": v.get("team", ""),
                "Линия": v.get("line", ""),

                "Коэфф. букмекера": price,
                "Вероятность модели": p_model,
                "Честный кэф (модель)": fair_odds,
                "Имплицитная вероятность (букм.)": implied_prob,
                "Перекос, %": edge_pct,
                "EV": ev,
                "Риск-скор": risk_score,
            })

    if not rows:
        print("Нет value-линий, нечего сохранять в Excel.")
        return

    df = pd.DataFrame(rows)

    # Сортировка по EV (от лучших к худшим)
    df = df.sort_values("EV", ascending=False).reset_index(drop=True)

    # Ранг по EV (1 — самая жирная ставка)
    df["Ранг по EV"] = df.index + 1

    # Гарантируем, что папка существует
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Полная таблица
    df.to_excel(filename, index=False)
    print(f"Полная таблица value сохранена в: {filename}")

    # Топ-20 только по положительному EV
    df_pos = df[df["EV"] > 0].copy()
    df_top20 = df_pos.nlargest(20, "EV")

    top20_xlsx = os.path.join(os.path.dirname(filename), "value_top20.xlsx")
    top20_json = os.path.join(os.path.dirname(filename), "value_top20.json")

    df_top20.to_excel(top20_xlsx, index=False)
    df_top20.to_json(top20_json, orient="records", force_ascii=False, indent=2)

    print(f"ТОП-20 value-линий сохранены в: {top20_xlsx}")
    print(f"ТОП-20 value-линий (JSON): {top20_json}")
