from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence

from core.context import GameContext


@dataclass
class ValueConfig:
    """Настройки для Value-модели."""
    min_edge_percent: float = 1.0     # минимальный Edge, чтобы допустить ставку
    kelly_fraction: float = 0.25      # Fractional Kelly (¼ Kelly)


class ValueModel:
    """Считает edge и Kelly для:
      - Moneyline
      - Totals (Over/Under)
      - Spread (Home/Away)
      - Team Totals (Home/Away)
    """

    def __init__(self, config: Optional[ValueConfig] = None):
        self.cfg = config or ValueConfig()

    # ------------------- UTILS -------------------

    @staticmethod
    def _implied_prob(odds: float) -> float:
        """Перевод decimal odds → implied probability."""
        if not odds or odds <= 1.0:
            return 0.0
        return 1.0 / odds

    @staticmethod
    def _kelly(p: float, b: float) -> float:
        """Полная формула Kelly."""
        q = 1 - p
        edge = b * p - q
        if b <= 0 or edge <= 0:
            return 0.0
        return edge / b

    def _compute_edge_kelly(self, p_model: float, odds: float) -> tuple[float, float]:
        """Возвращает (edge%, fractional_kelly)."""
        implied = self._implied_prob(odds)
        edge = (p_model - implied) * 100

        b = odds - 1
        k_full = self._kelly(p_model, b)
        k_fractional = max(0, k_full * self.cfg.kelly_fraction)

        if abs(edge) < self.cfg.min_edge_percent:
            k_fractional = 0.0

        return edge, k_fractional

    @staticmethod
    def _prob_from_distribution(dist: Sequence[float], predicate) -> float:
        if not dist:
            return 0.0
        return sum(1 for x in dist if predicate(x)) / float(len(dist))

    # ------------------- PROCESS -------------------

    def process(self, context: GameContext):
        """Главный метод Value-модели."""

        # ---------------------------------------------------------
        # 1) MONEYLINE
        # ---------------------------------------------------------
        p_home = context.model_outputs.get("mc_win_prob_home") \
                 or context.model_outputs.get("win_prob_home")

        p_away = context.model_outputs.get("mc_win_prob_away") \
                 or context.model_outputs.get("win_prob_away")

        odds_home = context.features.get("odds_home")
        odds_away = context.features.get("odds_away")

        if p_home is not None and odds_home:
            edge_home, kelly_home = self._compute_edge_kelly(p_home, odds_home)
            context.set_output("edge_home", edge_home)
            context.set_output("kelly_home", kelly_home)

        if p_away is not None and odds_away:
            edge_away, kelly_away = self._compute_edge_kelly(p_away, odds_away)
            context.set_output("edge_away", edge_away)
            context.set_output("kelly_away", kelly_away)

        # ---------------------------------------------------------
        # 2) TOTAL (Over / Under)
        # ---------------------------------------------------------
        total_line = context.features.get("total_line")
        total_over_odds = context.features.get("total_over_odds")
        total_under_odds = context.features.get("total_under_odds")
        total_dist = context.model_outputs.get("mc_total_distribution")

        if total_line is not None and total_dist:
            p_over = self._prob_from_distribution(total_dist, lambda x: x > total_line)
            p_under = 1 - p_over

            context.set_output("P_total_over", p_over)
            context.set_output("P_total_under", p_under)

            if total_over_odds:
                edge_o, k_o = self._compute_edge_kelly(p_over, total_over_odds)
                context.set_output("total_edge_over", edge_o)
                context.set_output("total_kelly_over", k_o)

            if total_under_odds:
                edge_u, k_u = self._compute_edge_kelly(p_under, total_under_odds)
                context.set_output("total_edge_under", edge_u)
                context.set_output("total_kelly_under", k_u)

        # ---------------------------------------------------------
        # 3) SPREAD (handicap)
        # ---------------------------------------------------------
        spread_line = context.features.get("spread_line")
        spread_odds_home = context.features.get("spread_odds_home")
        spread_odds_away = context.features.get("spread_odds_away")
        diff_dist = context.model_outputs.get("mc_diff_distribution")

        if spread_line is not None and diff_dist:
            p_home_cover = self._prob_from_distribution(diff_dist, lambda d: d > spread_line)
            p_away_cover = self._prob_from_distribution(diff_dist, lambda d: d < spread_line)

            context.set_output("P_spread_home_cover", p_home_cover)
            context.set_output("P_spread_away_cover", p_away_cover)

            if spread_odds_home:
                e, k = self._compute_edge_kelly(p_home_cover, spread_odds_home)
                context.set_output("spread_edge_home", e)
                context.set_output("spread_kelly_home", k)

            if spread_odds_away:
                e, k = self._compute_edge_kelly(p_away_cover, spread_odds_away)
                context.set_output("spread_edge_away", e)
                context.set_output("spread_kelly_away", k)

        # ---------------------------------------------------------
        # 4) TEAM TOTAL HOME
        # ---------------------------------------------------------
        home_tt = context.features.get("home_team_total")
        home_tt_over = context.features.get("home_team_total_over_odds")
        home_tt_under = context.features.get("home_team_total_under_odds")
        home_pts_dist = context.model_outputs.get("mc_home_pts_distribution")

        if home_tt is not None and home_pts_dist:
            p_over = self._prob_from_distribution(home_pts_dist, lambda x: x > home_tt)
            p_under = 1 - p_over

            context.set_output("P_home_team_total_over", p_over)
            context.set_output("P_home_team_total_under", p_under)

            if home_tt_over:
                e, k = self._compute_edge_kelly(p_over, home_tt_over)
                context.set_output("home_team_total_edge_over", e)
                context.set_output("home_team_total_kelly_over", k)

            if home_tt_under:
                e, k = self._compute_edge_kelly(p_under, home_tt_under)
                context.set_output("home_team_total_edge_under", e)
                context.set_output("home_team_total_kelly_under", k)

        # ---------------------------------------------------------
        # 5) TEAM TOTAL AWAY
        # ---------------------------------------------------------
        away_tt = context.features.get("away_team_total")
        away_tt_over = context.features.get("away_team_total_over_odds")
        away_tt_under = context.features.get("away_team_total_under_odds")
        away_pts_dist = context.model_outputs.get("mc_away_pts_distribution")

        if away_tt is not None and away_pts_dist:
            p_over = self._prob_from_distribution(away_pts_dist, lambda x: x > away_tt)
            p_under = 1 - p_over

            context.set_output("P_away_team_total_over", p_over)
            context.set_output("P_away_team_total_under", p_under)

            if away_tt_over:
                e, k = self._compute_edge_kelly(p_over, away_tt_over)
                context.set_output("away_team_total_edge_over", e)
                context.set_output("away_team_total_kelly_over", k)

            if away_tt_under:
                e, k = self._compute_edge_kelly(p_under, away_tt_under)
                context.set_output("away_team_total_edge_under", e)
                context.set_output("away_team_total_kelly_under", k)
