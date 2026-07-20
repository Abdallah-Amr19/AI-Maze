"""Greedy best-first search implementation for maze solving."""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set

from backend.algorithms.base import (
    PrioritizedNode,
    build_result,
    manhattan_distance,
)
from backend.models.maze import Coordinate, MazeConfig


def solve(maze: MazeConfig) -> Dict[str, object]:
    """Solve the maze using Greedy Best-First Search."""
    open_heap: List[PrioritizedNode] = []
    came_from: Dict[Coordinate, Optional[Coordinate]] = {maze.start: None}
    visited: Set[Coordinate] = set()
    expanded_order: List[List[int]] = []
    generated_nodes = 1
    frontier_peak = 1
    tie_breaker = 0

    heapq.heappush(
        open_heap,
        PrioritizedNode(
            priority=manhattan_distance(maze.start, maze.goal),
            tie_breaker=tie_breaker,
            position=maze.start,
        ),
    )

    while open_heap:
        current = heapq.heappop(open_heap).position
        if current in visited:
            continue

        visited.add(current)
        expanded_order.append([current[0], current[1]])

        if current == maze.goal:
            return build_result(
                maze=maze,
                algorithm="greedy",
                found=True,
                came_from=came_from,
                expanded_order=expanded_order,
                closed_set=visited,
                generated_nodes=generated_nodes,
                frontier_peak=frontier_peak,
            )

        for neighbor in maze.neighbors(current):
            if neighbor in visited:
                continue

            if neighbor not in came_from:
                came_from[neighbor] = current
            tie_breaker += 1
            heapq.heappush(
                open_heap,
                PrioritizedNode(
                    priority=manhattan_distance(neighbor, maze.goal),
                    tie_breaker=tie_breaker,
                    position=neighbor,
                ),
            )
            generated_nodes += 1
            frontier_peak = max(frontier_peak, len(open_heap))

    return build_result(
        maze=maze,
        algorithm="greedy",
        found=False,
        came_from=came_from,
        expanded_order=expanded_order,
        closed_set=visited,
        generated_nodes=generated_nodes,
        frontier_peak=frontier_peak,
    )
