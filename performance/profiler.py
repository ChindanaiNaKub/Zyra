"""Performance profiler for detailed timing analysis.

This module provides profiling capabilities to identify performance
bottlenecks in search, evaluation, and core operations.
"""

import functools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ProfilerContext:
    """Context for performance profiling."""

    enabled: bool = False
    detailed_timing: bool = False
    memory_profiling: bool = False
    call_stack_depth: int = 0
    max_depth: int = 10

    def __enter__(self):
        self.call_stack_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.call_stack_depth -= 1


class PerformanceProfiler:
    """Profiler for detailed performance analysis."""

    def __init__(self):
        self.context = ProfilerContext()
        self.timings: Dict[str, List[float]] = {}
        self.call_counts: Dict[str, int] = {}
        self.memory_snapshots: List[Dict[str, float]] = []

    def enable(self, detailed: bool = False, memory: bool = False) -> None:
        """Enable profiling with optional detailed timing and memory tracking."""
        self.context.enabled = True
        self.context.detailed_timing = detailed
        self.context.memory_profiling = memory

    def disable(self) -> None:
        """Disable profiling."""
        self.context.enabled = False
        self.context.detailed_timing = False
        self.context.memory_profiling = False

    def profile_function(self, name: Optional[str] = None):
        """Decorator to profile function execution time."""

        def decorator(func: Callable) -> Callable:
            func_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.context.enabled:
                    return func(*args, **kwargs)

                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start_time
                    self._record_timing(func_name, duration)

            return wrapper

        return decorator

    def profile_method(self, name: Optional[str] = None):
        """Decorator to profile method execution time."""

        def decorator(func: Callable) -> Callable:
            func_name = name or f"{func.__qualname__}"

            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if not self.context.enabled:
                    return func(self, *args, **kwargs)

                start_time = time.perf_counter()
                try:
                    result = func(self, *args, **kwargs)
                    return result
                finally:
                    duration = time.perf_counter() - start_time
                    self._record_timing(func_name, duration)

            return wrapper

        return decorator

    def _record_timing(self, name: str, duration: float) -> None:
        """Record timing for a function call."""
        if name not in self.timings:
            self.timings[name] = []
            self.call_counts[name] = 0

        self.timings[name].append(duration)
        self.call_counts[name] += 1

    def get_timing_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of timing data."""
        summary = {}

        for name, timings in self.timings.items():
            if not timings:
                continue

            total_time = sum(timings)
            avg_time = total_time / len(timings)
            min_time = min(timings)
            max_time = max(timings)

            summary[name] = {
                "total_time_ms": total_time * 1000,
                "avg_time_ms": avg_time * 1000,
                "min_time_ms": min_time * 1000,
                "max_time_ms": max_time * 1000,
                "call_count": self.call_counts[name],
                "calls_per_second": self.call_counts[name] / total_time if total_time > 0 else 0,
            }

        return summary

    def get_slowest_functions(self, limit: int = 10) -> List[tuple]:
        """Get the slowest functions by total time."""
        summary = self.get_timing_summary()
        return sorted(summary.items(), key=lambda x: x[1]["total_time_ms"], reverse=True)[:limit]

    def get_hotspots(self, limit: int = 10) -> List[tuple]:
        """Get functions with highest call frequency."""
        summary = self.get_timing_summary()
        return sorted(summary.items(), key=lambda x: x[1]["call_count"], reverse=True)[:limit]

    def clear_data(self) -> None:
        """Clear all profiling data."""
        self.timings.clear()
        self.call_counts.clear()
        self.memory_snapshots.clear()

    def export_data(self) -> Dict[str, Any]:
        """Export profiling data for analysis."""
        return {
            "timing_summary": self.get_timing_summary(),
            "slowest_functions": self.get_slowest_functions(),
            "hotspots": self.get_hotspots(),
            "context": {
                "enabled": self.context.enabled,
                "detailed_timing": self.context.detailed_timing,
                "memory_profiling": self.context.memory_profiling,
            },
        }


# Global profiler instance
_global_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return _global_profiler


def profile_function(name: Optional[str] = None):
    """Convenience function to profile a function."""
    return _global_profiler.profile_function(name)


def profile_method(name: Optional[str] = None):
    """Convenience function to profile a method."""
    return _global_profiler.profile_method(name)


def enable_profiling(detailed: bool = False, memory: bool = False) -> None:
    """Enable global profiling."""
    _global_profiler.enable(detailed, memory)


def disable_profiling() -> None:
    """Disable global profiling."""
    _global_profiler.disable()


def get_profiling_summary() -> Dict[str, Any]:
    """Get profiling summary."""
    return _global_profiler.export_data()
