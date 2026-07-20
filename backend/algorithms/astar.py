"""A* graph search implementation for maze solving."""

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
    """Solve the maze using optimal A* graph search."""
    open_heap: List[PrioritizedNode] = []
    came_from: Dict[Coordinate, Optional[Coordinate]] = {maze.start: None}
    g_scores: Dict[Coordinate, int] = {maze.start: 0}
    closed_set: Set[Coordinate] = set()
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
        if current in closed_set:
            continue

        closed_set.add(current)
        expanded_order.append([current[0], current[1]])

        if current == maze.goal:
            return build_result(
                maze=maze,
                algorithm="astar",
                found=True,
                came_from=came_from,
                expanded_order=expanded_order,
                closed_set=closed_set,
                generated_nodes=generated_nodes,
                frontier_peak=frontier_peak,
            )

        for neighbor in maze.neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_cost = g_scores[current] + 1
            if tentative_cost < g_scores.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_scores[neighbor] = tentative_cost
                tie_breaker += 1
                heapq.heappush(
                    open_heap,
                    PrioritizedNode(
                        priority=tentative_cost + manhattan_distance(neighbor, maze.goal),
                        tie_breaker=tie_breaker,
                        position=neighbor,
                    ),
                )
                generated_nodes += 1
                frontier_peak = max(frontier_peak, len(open_heap))

    return build_result(
        maze=maze,
        algorithm="astar",
        found=False,
        came_from=came_from,
        expanded_order=expanded_order,
        closed_set=closed_set,
        generated_nodes=generated_nodes,
        frontier_peak=frontier_peak,
    )
