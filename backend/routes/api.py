"""REST API endpoints for maze generation and search."""

from __future__ import annotations

from typing import Callable, Dict

from flask import Blueprint, jsonify, request

from backend.algorithms import astar, bfs, dfs, greedy
from backend.utils.maze_generator import generate_maze
from backend.utils.profiler import measure_execution
from backend.utils.validation import (
    validate_algorithm,
    validate_generate_payload,
    validate_maze_payload,
)

api_blueprint = Blueprint("api", __name__)

SOLVERS: Dict[str, Callable] = {
    "astar": astar.solve,
    "bfs": bfs.solve,
    "dfs": dfs.solve,
    "greedy": greedy.solve,
}


@api_blueprint.route("/health", methods=["GET"])
def health_check():
    """Basic health endpoint for quick runtime verification."""
    return jsonify({"status": "ok", "service": "maze-navigation-api"})


@api_blueprint.route("/generate-maze", methods=["POST"])
def generate_maze_endpoint():
    """Create a random maze for the frontend visualizer."""
    payload = request.get_json(silent=True) or {}
    settings = validate_generate_payload(payload)
    maze = generate_maze(**settings)
    return jsonify({"success": True, "maze": maze})


@api_blueprint.route("/solve", methods=["POST"])
def solve_endpoint():
    """Solve a maze using a selected search algorithm."""
    payload = request.get_json(silent=True) or {}
    maze = validate_maze_payload(payload)
    algorithm = validate_algorithm(payload.get("algorithm", "astar"))
    profile = measure_execution(lambda: SOLVERS[algorithm](maze))
    result = profile["result"]
    result["metrics"]["execution_time_ms"] = profile["execution_time_ms"]
    result["metrics"]["memory_kb"] = profile["memory_kb"]
    return jsonify({"success": True, "result": result})


@api_blueprint.route("/compare", methods=["POST"])
def compare_endpoint():
    """Run multiple algorithms on the same maze and return all results."""
    payload = request.get_json(silent=True) or {}
    maze = validate_maze_payload(payload)
    algorithms = payload.get("algorithms", ["astar", "bfs", "dfs", "greedy"])

    if not isinstance(algorithms, list) or not algorithms:
        raise ValueError("algorithms must be a non-empty array.")

    results = []
    for algorithm_name in algorithms:
        normalized_name = validate_algorithm(algorithm_name)
        profile = measure_execution(lambda n=normalized_name: SOLVERS[n](maze))
        result = profile["result"]
        result["metrics"]["execution_time_ms"] = profile["execution_time_ms"]
        result["metrics"]["memory_kb"] = profile["memory_kb"]
        results.append(result)

    results.sort(
        key=lambda item: (
            not item["found"],
            item["metrics"]["path_cost"]
            if item["metrics"]["path_cost"] is not None
            else float("inf"),
            item["metrics"]["execution_time_ms"],
        )
    )
    return jsonify({"success": True, "results": results})
