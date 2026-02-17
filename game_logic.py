"""Core game logic utilities for Kash Card Game.

Functions here are independent of Flask so they can be reused by a CLI or tests.
"""
from typing import List, Dict, Tuple, Optional

LOSING_SCORE = 21

def determine_required(players: List[str], dealer_index: int) -> Dict[str, int]:
    dealer = players[dealer_index]
    suit_chooser = players[(dealer_index + 1) % 3]
    other = players[(dealer_index + 2) % 3]
    return {dealer: 3, suit_chooser: 8, other: 5}


def compute_round(scores: Dict[str, int], players: List[str], required: Dict[str, int], actual: Dict[str, int]) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, Dict[str, int]]]:
    """Apply scoring for a round.

    Returns (updated_scores, missing, pending_swaps).
    - `scores` is mutated in-place and returned for convenience.
    - `missing` is a dict player->missing count (points added).
    - `pending_swaps` maps debtor->{creditor:count} for next round.
    """
    missing: Dict[str, int] = {}
    for p in players:
        miss = max(0, required.get(p, 0) - actual.get(p, 0))
        missing[p] = miss
        scores[p] = scores.get(p, 0) + miss

    extra: Dict[str, int] = {p: max(0, actual.get(p, 0) - required.get(p, 0)) for p in players}

    pending_swaps: Dict[str, Dict[str, int]] = {}
    for debtor in players:
        need = missing.get(debtor, 0)
        if need == 0:
            continue
        remaining = need
        # Distribute from others who have extras
        for creditor in players:
            if creditor == debtor:
                continue
            if remaining == 0:
                break
            available = extra.get(creditor, 0)
            if available <= 0:
                continue
            take = min(remaining, available)
            pending_swaps.setdefault(debtor, {})[creditor] = pending_swaps[debtor].get(creditor, 0) + take
            extra[creditor] = available - take
            remaining -= take
        # If remaining > 0, nothing else to do here (warning could be logged by caller)

    return scores, missing, pending_swaps


def check_loser(scores: Dict[str, int], losing_score: int = LOSING_SCORE) -> Optional[str]:
    for p, s in scores.items():
        if s >= losing_score:
            return p
    return None


def rotate_dealer(dealer_index: int) -> int:
    return (dealer_index + 1) % 3
