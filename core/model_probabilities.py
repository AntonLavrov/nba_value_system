import math
from math import erf, sqrt


# -----------------------------
# Нормальное распределение
# -----------------------------
def normal_cdf(x, mu=0, sigma=1):
    return 0.5 * (1 + erf((x - mu) / (sigma * math.sqrt(2))))


# -----------------------------
# Вероятность победы через логистику NBA
# -----------------------------
def logistic_win_probability(xMargin):
    """
    Вероятность победы фаворита через xMargin.
    Формула классическая NBA: 10^(margin/6)
    """
    return 1 / (1 + 10 ** (-xMargin / 6))


# -----------------------------
# Вероятность Тотала
# -----------------------------
def probability_total(xTOTAL, line, side="over", sigma=15.5):
    """
    xTOTAL — ожидаемый тотал
    line — линия тотала
    side — over / under
    """

    if side == "over":
        return 1 - normal_cdf(line, mu=xTOTAL, sigma=sigma)

    elif side == "under":
        return normal_cdf(line, mu=xTOTAL, sigma=sigma)

    else:
        raise ValueError("side must be 'over' or 'under'")


# -----------------------------
# Вероятность покрытия форы
# -----------------------------
def probability_team_total(xMargin, line, side="home", sigma=11):
    """
    xMargin — ожидаемая разница home - away
    line — фора, как она приходит из БК:
        для фаворита дома обычно отрицательная (например -6.5),
        для андердога положительная (+6.5).
    side — 'home' или 'away'
    """

    # ставка на домашнюю команду:
    # линия line (например -6.5) → нужно победить больше, чем на abs(line)
    if side == "home":
        threshold = -line  # если line = -6.5 → threshold = 6.5
        return 1 - normal_cdf(threshold, mu=xMargin, sigma=sigma)

    # ставка на гостевую:
    # линия line (например +6.5) → нужно "держать" счёт: M < line
    elif side == "away":
        threshold = line  # для +6.5
        return normal_cdf(threshold, mu=xMargin, sigma=sigma)

    else:
        raise ValueError("side must be 'home' or 'away'")
