"""Helpers for timing and memory profiling of search algorithms."""

from __future__ import annotations

import time
import tracemalloc
from typing import Callable, Dict, TypeVar

T = TypeVar("T")


def measure_execution(operation: Callable[[], T]) -> Dict[str, object]:
    """Run an operation and capture timing plus peak memory usage."""
    tracemalloc.start()
    start_time = time.perf_counter()
    result = operation()
    execution_time_ms = (time.perf_counter() - start_time) * 1000
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "result": result,
        "execution_time_ms": round(execution_time_ms, 3),
        "memory_kb": round(peak_memory / 1024, 3),
    }
