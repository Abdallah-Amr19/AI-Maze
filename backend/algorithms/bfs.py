"""Breadth-first search implementation for maze solving."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional, Set

from backend.algorithms.base import build_result
from backend.models.maze import Coordinate, MazeConfig


def solve(maze: MazeConfig) -> Dict[str, object]:
    """Solve the maze using BFS graph search."""
    queue: Deque[Coordinate] = deque([maze.start])
    came_from: Dict[Coordinate, Optional[Coordinate]] = {maze.start: None}
    visited: Set[Coordinate] = {maze.start}
    expanded_order: List[List[int]] = []
    generated_nodes = 1
    frontier_peak = 1

    while queue:
        current = queue.popleft()
        expanded_order.append([current[0], current[1]])

        if current == maze.goal:
            return build_result(
                maze=maze,
                algorithm="bfs",
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
            visited.add(neighbor)
            came_from[neighbor] = current
            queue.append(neighbor)
            generated_nodes += 1
            frontier_peak = max(frontier_peak, len(queue))

    return build_result(
        maze=maze,
        algorithm="bfs",
        found=False,
        came_from=came_from,
        expanded_order=expanded_order,
        closed_set=visited,
        generated_nodes=generated_nodes,
        frontier_peak=frontier_peak,
    )
