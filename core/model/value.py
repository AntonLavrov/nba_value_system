# core/model/value.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from core.context import GameContext


@dataclass
class ValueConfig:
    """
    Настройки для Value-модели.
    """
    min_edge_percent: float = 1.0   # минимальный % перевеса, чтобы считать ставку интересной
    kelly_fraction: float = 0.25    # доля от полного Kelly (0.25 = четверть Келли)


class ValueModel:
    """
    Сравнивает вероятности модели с рыночными коэффициентами и
    считает 'value' и долю Kelly.
    """

    def __init__(self, config: Optional[ValueConfig] = None):
        self.cfg = config or ValueConfig()

    @staticmethod
    def _implied_prob(odds: float) -> float:
        """
        Перевод decimal-коэффициента в подразумеваемую вероятность.
        """
        if odds <= 1.0:
            return 0.0
        return 1.0 / odds

    @staticmethod
    def _kelly_fraction(p: float, q: float, b: float) -> float:
        """
        Формула Келли:
        f* = (bp - q) / b
        где:
          b = k - 1 (k - коэффициент),
          p = вероятность выигрыша,
          q = 1 - p
        """
        edge = b * p - q
        if b <= 0 or edge <= 0:
            return 0.0
        return edge / b

    def process(self, context: GameContext):
        """
        Основной метод для pipeline.
        Ожидает, что в context.model_outputs есть win_prob_*,
        а в context.features лежат odds_home/odds_away.
        """

        # вероятности модели
        p_home = context.model_outputs.get("mc_win_prob_home") \
                 or context.model_outputs.get("win_prob_home")
        p_away = context.model_outputs.get("mc_win_prob_away") \
                 or context.model_outputs.get("win_prob_away")

        if p_home is None or p_away is None:
            # если модель не посчитала вероятности — ничего не делаем
            return

        # коэффициенты рынка
        odds_home = context.features.get("odds_home")
        odds_away = context.features.get("odds_away")

        if odds_home is None or odds_away is None:
            # без коэффициентов нечего считать
            return

        # подразумеваемые вероятности
        imp_home = self._implied_prob(odds_home)
        imp_away = self._implied_prob(odds_away)

        # edge в процентах
        edge_home = (p_home - imp_home) * 100.0
        edge_away = (p_away - imp_away) * 100.0

        # Kelly
        b_home = odds_home - 1.0
        b_away = odds_away - 1.0

        kelly_home_full = self._kelly_fraction(p_home, 1.0 - p_home, b_home)
        kelly_away_full = self._kelly_fraction(p_away, 1.0 - p_away, b_away)

        kelly_home = max(0.0, kelly_home_full * self.cfg.kelly_fraction)
        kelly_away = max(0.0, kelly_away_full * self.cfg.kelly_fraction)

        # фильтр по минимальному edge (по желанию)
        if abs(edge_home) < self.cfg.min_edge_percent:
            kelly_home = 0.0
        if abs(edge_away) < self.cfg.min_edge_percent:
            kelly_away = 0.0

        context.set_output("edge_home", edge_home)
        context.set_output("edge_away", edge_away)
        context.set_output("kelly_home", kelly_home)
        context.set_output("kelly_away", kelly_away)
