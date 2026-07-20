"""Shared search utilities and result formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from backend.models.maze import Coordinate, MazeConfig


@dataclass(order=True)
class PrioritizedNode:
    """Priority queue item used by informed search algorithms."""

    priority: int
    tie_breaker: int
    position: Coordinate = field(compare=False)


def manhattan_distance(current: Coordinate, goal: Coordinate) -> int:
    """Admissible heuristic for four-directional grid movement."""
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def reconstruct_path(
    came_from: Dict[Coordinate, Optional[Coordinate]],
    goal: Coordinate,
) -> List[List[int]]:
    """Backtrack from the goal to produce the final path."""
    path: List[List[int]] = []
    current: Optional[Coordinate] = goal

    while current is not None:
        path.append([current[0], current[1]])
        current = came_from[current]

    path.reverse()
    return path


def build_result(
    maze: MazeConfig,
    algorithm: str,
    found: bool,
    came_from: Dict[Coordinate, Optional[Coordinate]],
    expanded_order: List[List[int]],
    closed_set: Set[Coordinate],
    generated_nodes: int,
    frontier_peak: int,
) -> Dict[str, object]:
    """Build a consistent response payload for every algorithm."""
    path = reconstruct_path(came_from, maze.goal) if found else []
    path_cost = max(0, len(path) - 1) if path else None

    return {
        "algorithm": algorithm,
        "found": found,
        "path": path,
        "explored_order": expanded_order,
        "metrics": {
            "path_cost": path_cost,
            "expanded_nodes": len(expanded_order),
            "generated_nodes": generated_nodes,
            "closed_set_size": len(closed_set),
            "frontier_peak": frontier_peak,
        },
    }
