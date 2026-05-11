from __future__ import annotations

from dataclasses import replace

from trading_agent.models import EntryType, Zone


def score_zone(zone: Zone) -> Zone:
    freshness = _freshness_score(zone.tested_count)
    legout = _legout_score(zone)
    base = _base_score(zone.base_count)
    return replace(zone, score=round(freshness + legout + base, 2), fresh=zone.tested_count == 0)


def entry_type_for_score(score: float) -> EntryType | None:
    if score >= 7:
        return EntryType.SET_AND_FORGET
    if score >= 6:
        return EntryType.CONFIRMATION_CLOSE_OPEN
    if score >= 5:
        return EntryType.CONFIRMATION_LEAVE_ZONE
    return None


def _freshness_score(tested_count: int) -> float:
    if tested_count <= 0:
        return 3.0
    if tested_count == 1:
        return 1.5
    return 0.0


def _legout_score(zone: Zone) -> float:
    if zone.has_gap or zone.legout_strength == "very_strong":
        return 2.0
    if zone.legout_strength == "strong":
        return 1.5
    return 1.0


def _base_score(base_count: int) -> float:
    if 1 <= base_count <= 3:
        return 2.0
    if 4 <= base_count <= 5:
        return 1.0
    return 0.0
