# core/features/motivation.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Dict

from core.context import GameContext
from parsers.standings_parser import load_standings


@dataclass
class MotivationConfig:
    """
    Настройки для расчёта мотивации.
    """
    playoff_bubble_boost: float = 1.5    # 6–10 место на Западе/Востоке
    top_seed_relax_penalty: float = -0.7 # топ-2 могут "экономить силы"
    tanking_penalty: float = -2.5        # дно таблицы в конце сезона
    rivalry_bonus: float = 0.8           # для "важных" матчей (позже можно расширить)
    late_season_month: int = 3           # с какого месяца считать "конец сезона" (март)


class MotivationModule:
    """
    Модуль, который оценивает мотивацию команд
    на основе турнирного положения и даты.
    """

    def __init__(self, config: MotivationConfig | None = None):
        self.cfg = config or MotivationConfig()
        # { "LAL": {"conference_rank": 8, "wins": ..., "losses": ...}, ... }
        self.standings: Dict[str, Dict[str, int]] = load_standings()

    # ----------------------------------------------------------

    def _compute_team_motivation(self, team: str, game_date: date, opponent: str | None = None) -> float:
        info = self.standings.get(team)
        if not info:
            return 0.0

        rank = info.get("conference_rank", 0)
        wins = info.get("wins", 0)
        losses = info.get("losses", 0)
        games_played = wins + losses

        mot = 0.0

        # Ранний сезон — мотивация более-менее ровная
        if games_played < 20:
            return 0.0

        # Конец сезона?
        is_late_season = game_date.month >= self.cfg.late_season_month

        # Bubble / плей-ин зона (места примерно 6–10)
        if 6 <= rank <= 10:
            mot += self.cfg.playoff_bubble_boost

        # Топ-2 — могут быть менее заряжены в регулярке, особенно в конце
        if rank in (1, 2) and is_late_season:
            mot += self.cfg.top_seed_relax_penalty

        # Дно конференции — могут "танковать" ближе к концу
        if rank >= 13 and is_late_season:
            mot += self.cfg.tanking_penalty

        # Матч с близким по таблице соперником (условная "важность")
        if opponent is not None:
            opp_info = self.standings.get(opponent)
            if opp_info:
                opp_rank = opp_info.get("conference_rank", 0)
                # если разница в рангах мала, матч важный
                if abs(opp_rank - rank) <= 2:
                    mot += self.cfg.rivalry_bonus

        return mot

    # ----------------------------------------------------------

    def process(self, context: GameContext):
        """
        Основной метод для pipeline.
        """

        game_date = context.date

        home_motivation = self._compute_team_motivation(
            team=context.home,
            game_date=game_date,
            opponent=context.away,
        )
        away_motivation = self._compute_team_motivation(
            team=context.away,
            game_date=game_date,
            opponent=context.home,
        )

        context.add_feature("motivation_home", home_motivation)
        context.add_feature("motivation_away", away_motivation)
