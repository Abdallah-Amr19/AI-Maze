"""Maze domain models and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class MazeConfig:
    """Normalized maze configuration used by search algorithms."""

    grid: List[List[int]]
    start: Coordinate
    goal: Coordinate

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def in_bounds(self, position: Coordinate) -> bool:
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_walkable(self, position: Coordinate) -> bool:
        row, col = position
        return self.grid[row][col] == 0

    def neighbors(self, position: Coordinate) -> Iterable[Coordinate]:
        """Return valid four-directional neighbors."""
        row, col = position
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d_row, d_col in deltas:
            candidate = (row + d_row, col + d_col)
            if self.in_bounds(candidate) and self.is_walkable(candidate):
                yield candidate


def normalize_coordinate(value: Sequence[int], label: str) -> Coordinate:
    """Validate and normalize a coordinate payload."""
    if not isinstance(value, Sequence) or len(value) != 2:
        raise ValueError(f"{label} must contain exactly two integers.")

    row, col = value
    if not isinstance(row, int) or not isinstance(col, int):
        raise ValueError(f"{label} values must be integers.")

    return row, col
