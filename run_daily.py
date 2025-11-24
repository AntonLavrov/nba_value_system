from engine.day_processor import run_day
from engine.export import export_to_excel
import json


if __name__ == "__main__":
    results = run_day()

    with open("outputs/value_today.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    export_to_excel(results, "outputs/value_today.xlsx")

    print("\n=== Value-ставки сохранены в outputs/value_today.json и value_today.xlsx ===")
