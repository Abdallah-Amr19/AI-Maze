"""Random maze generation utilities."""

from __future__ import annotations

import random
from typing import Dict, List, Tuple


Coordinate = Tuple[int, int]


def generate_maze(rows: int, cols: int, density: float = 0.2) -> Dict[str, object]:
    """
    Generate a maze using recursive backtracking, then add extra walls
    to create slightly different layouts for repeated demos.
    """
    grid: List[List[int]] = [[1 for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    stack = [start]
    grid[start[0]][start[1]] = 0

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        current_row, current_col = stack[-1]
        neighbors = []

        for d_row, d_col in directions:
            next_row = current_row + d_row
            next_col = current_col + d_col
            if 1 <= next_row < rows - 1 and 1 <= next_col < cols - 1:
                if grid[next_row][next_col] == 1:
                    neighbors.append((next_row, next_col, d_row // 2, d_col // 2))

        if neighbors:
            next_row, next_col, wall_row_delta, wall_col_delta = random.choice(neighbors)
            grid[current_row + wall_row_delta][current_col + wall_col_delta] = 0
            grid[next_row][next_col] = 0
            stack.append((next_row, next_col))
        else:
            stack.pop()

    _sprinkle_openings(grid, density)

    goal = _find_farthest_open_cell(grid, start)
    return {
        "grid": grid,
        "start": [start[0], start[1]],
        "goal": [goal[0], goal[1]],
    }


def _sprinkle_openings(grid: List[List[int]], density: float) -> None:
    """Add a small number of openings to reduce overly linear mazes."""
    rows = len(grid)
    cols = len(grid[0])
    candidates = [
        (row, col)
        for row in range(1, rows - 1)
        for col in range(1, cols - 1)
        if grid[row][col] == 1 and (row % 2 == 1 or col % 2 == 1)
    ]
    random.shuffle(candidates)

    extra_openings = int(len(candidates) * density)
    for row, col in candidates[:extra_openings]:
        grid[row][col] = 0


def _find_farthest_open_cell(grid: List[List[int]], start: Coordinate) -> Coordinate:
    """Choose a goal that tends to produce a longer, more interesting path."""
    from collections import deque

    rows = len(grid)
    cols = len(grid[0])
    queue = deque([(start, 0)])
    visited = {start}
    farthest = start
    max_distance = 0

    while queue:
        (row, col), distance = queue.popleft()
        if distance > max_distance:
            max_distance = distance
            farthest = (row, col)

        for next_row, next_col in (
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ):
            neighbor = (next_row, next_col)
            if (
                0 <= next_row < rows
                and 0 <= next_col < cols
                and grid[next_row][next_col] == 0
                and neighbor not in visited
            ):
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    return farthest
