"""Validation helpers for incoming API payloads."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.models.maze import MazeConfig, normalize_coordinate

SUPPORTED_ALGORITHMS = {"astar", "bfs", "dfs", "greedy"}


def validate_grid(grid: Any) -> List[List[int]]:
    """Ensure the maze grid is a rectangular matrix of 0/1 integers."""
    if not isinstance(grid, list) or not grid:
        raise ValueError("Maze grid must be a non-empty 2D array.")

    if not all(isinstance(row, list) and row for row in grid):
        raise ValueError("Each maze row must be a non-empty list.")

    row_length = len(grid[0])
    if row_length < 2:
        raise ValueError("Maze must contain at least two columns.")

    normalized_grid: List[List[int]] = []
    for row_index, row in enumerate(grid):
        if len(row) != row_length:
            raise ValueError("Maze grid must be rectangular.")

        normalized_row: List[int] = []
        for col_index, cell in enumerate(row):
            if cell not in (0, 1):
                raise ValueError(
                    f"Invalid cell value at ({row_index}, {col_index}). "
                    "Use 0 for open cells and 1 for walls."
                )
            normalized_row.append(int(cell))
        normalized_grid.append(normalized_row)

    return normalized_grid


def validate_maze_payload(payload: Dict[str, Any]) -> MazeConfig:
    """Validate the maze solve payload and return a normalized config."""
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    grid = validate_grid(payload.get("grid"))
    start = normalize_coordinate(payload.get("start"), "start")
    goal = normalize_coordinate(payload.get("goal"), "goal")

    maze = MazeConfig(grid=grid, start=start, goal=goal)

    for label, coordinate in (("start", maze.start), ("goal", maze.goal)):
        if not maze.in_bounds(coordinate):
            raise ValueError(f"{label} must be inside the maze boundaries.")
        if not maze.is_walkable(coordinate):
            raise ValueError(f"{label} must be placed on an open cell.")

    return maze


def validate_algorithm(name: Any) -> str:
    """Validate a requested algorithm identifier."""
    if not isinstance(name, str):
        raise ValueError("Algorithm must be a string.")

    normalized = name.strip().lower()
    if normalized not in SUPPORTED_ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm '{name}'. "
            f"Supported values: {', '.join(sorted(SUPPORTED_ALGORITHMS))}."
        )

    return normalized


def validate_generate_payload(payload: Dict[str, Any]) -> Dict[str, int]:
    """Validate random maze generation settings."""
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    rows = int(payload.get("rows", 21))
    cols = int(payload.get("cols", 21))
    density = float(payload.get("density", 0.2))

    if rows < 7 or cols < 7:
        raise ValueError("Maze dimensions must be at least 7 x 7.")
    if rows > 61 or cols > 61:
        raise ValueError("Maze dimensions must be at most 61 x 61 for demo use.")
    if density < 0 or density > 0.45:
        raise ValueError("Density must be between 0 and 0.45.")

    rows = rows if rows % 2 == 1 else rows + 1
    cols = cols if cols % 2 == 1 else cols + 1

    return {"rows": rows, "cols": cols, "density": density}
