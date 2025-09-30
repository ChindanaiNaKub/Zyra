"""Lightweight transposition table for MCTS.

Stores aggregate statistics keyed by Zobrist hash. Replacement policy is simple
bucketed LRU via insertion order within a fixed-size dict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TTEntry:
    visits: int
    value: float


class TranspositionTable:
    def __init__(self, max_entries: int = 1_000_000) -> None:
        self._table: Dict[int, TTEntry] = {}
        self._max = max(1024, max_entries)

    def get(self, key: int) -> Optional[TTEntry]:
        return self._table.get(key)

    def store(self, key: int, visits: int, value: float) -> None:
        if key in self._table:
            # Merge by summing visits and values
            entry = self._table[key]
            entry.visits += visits
            entry.value += value
            return
        if len(self._table) >= self._max:
            # Evict an arbitrary item (FIFO-ish). For simplicity, pop first key.
            try:
                first_key = next(iter(self._table))
                self._table.pop(first_key, None)
            except StopIteration:
                pass
        self._table[key] = TTEntry(visits=visits, value=value)
