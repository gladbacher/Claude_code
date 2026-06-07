"""Kelly staking and bankroll management."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Bet:
    match: str
    market: str
    model_p: float
    decimal_odds: float
    stake: float
    edge: float
    result: Optional[bool] = None  # True = won, False = lost, None = pending

    @property
    def pnl(self) -> float:
        if self.result is True:
            return self.stake * (self.decimal_odds - 1.0)
        if self.result is False:
            return -self.stake
        return 0.0


class BankrollManager:
    """Full-Kelly staking capped at max_kelly_fraction of current bankroll."""

    def __init__(
        self,
        bankroll: float,
        max_kelly_fraction: float = 0.25,
        min_edge: float = 0.05,
        vig: float = 0.047,
    ) -> None:
        self.bankroll = bankroll
        self.max_kelly = max_kelly_fraction
        self.min_edge = min_edge
        self.vig = vig
        self.bets: list[Bet] = []

    def kelly_stake(self, model_p: float, decimal_odds: float) -> tuple[float, float]:
        """
        Compute stake and edge for a bet.

        Returns (stake, edge). Stake is 0 when edge is below min_edge.
        """
        implied = 1.0 / decimal_odds
        edge = model_p - implied - self.vig
        if edge < self.min_edge:
            return 0.0, edge

        b = decimal_odds - 1.0
        kelly_f = edge / b if b > 0 else 0.0
        capped_f = min(kelly_f, self.max_kelly)
        stake = round(self.bankroll * capped_f, 2)
        return stake, round(edge, 4)

    def log_bet(
        self,
        match: str,
        market: str,
        model_p: float,
        decimal_odds: float,
        result: Optional[bool] = None,
    ) -> Bet | None:
        """Record a bet. Returns None if edge is below threshold."""
        stake, edge = self.kelly_stake(model_p, decimal_odds)
        if stake <= 0:
            logger.info("No value: %s %s edge=%.3f", match, market, edge)
            return None
        bet = Bet(
            match=match,
            market=market,
            model_p=model_p,
            decimal_odds=decimal_odds,
            stake=stake,
            edge=edge,
            result=result,
        )
        self.bets.append(bet)
        logger.info(
            "BET logged: %s | %s | stake=%.2f | odds=%.2f | edge=%.3f",
            match, market, stake, decimal_odds, edge,
        )
        return bet

    def settle(self, bet: Bet, won: bool) -> None:
        """Settle a bet and update bankroll."""
        bet.result = won
        self.bankroll += bet.pnl
        logger.info(
            "SETTLED: %s | %s | pnl=%.2f | bankroll=%.2f",
            bet.match, bet.market, bet.pnl, self.bankroll,
        )

    def summary(self) -> dict:
        """Return performance summary dict."""
        settled = [b for b in self.bets if b.result is not None]
        if not settled:
            return {"bets": 0, "bankroll": self.bankroll}

        total_staked = sum(b.stake for b in settled)
        total_pnl = sum(b.pnl for b in settled)
        wins = sum(1 for b in settled if b.result)
        roi = total_pnl / total_staked if total_staked > 0 else 0.0

        return {
            "bets": len(settled),
            "wins": wins,
            "win_rate": wins / len(settled),
            "total_staked": round(total_staked, 2),
            "total_pnl": round(total_pnl, 2),
            "roi": round(roi, 4),
            "bankroll": round(self.bankroll, 2),
        }

    def print_summary(self) -> None:
        s = self.summary()
        print(f"\n{'─'*40}")
        print(f"  Bets:        {s['bets']}")
        if s["bets"]:
            print(f"  Win rate:    {s['win_rate']:.1%}")
            print(f"  Staked:      £{s['total_staked']:.2f}")
            print(f"  P&L:         £{s['total_pnl']:+.2f}")
            print(f"  ROI:         {s['roi']:.1%}")
        print(f"  Bankroll:    £{s['bankroll']:.2f}")
        print(f"{'─'*40}\n")
