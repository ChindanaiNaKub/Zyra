"""Performance metrics collection and analysis.

This module provides infrastructure for collecting, storing, and analyzing
performance metrics to validate performance targets.
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    # Search metrics
    nodes_per_second: float = 0.0
    total_nodes: int = 0
    search_time_ms: float = 0.0

    # Evaluation metrics
    evaluation_time_ms: float = 0.0
    evaluations_per_second: float = 0.0
    total_evaluations: int = 0

    # Move generation metrics
    move_generation_time_ms: float = 0.0
    moves_generated: int = 0

    # Move validation metrics
    move_validation_time_ms: float = 0.0
    moves_validated: int = 0

    # Memory metrics
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0

    # Style performance consistency
    style_variance_percent: float = 0.0

    # Legacy field for backward compatibility with serialized data
    targets_met: Optional[Dict[str, bool]] = None

    def __post_init__(self):
        """Handle legacy targets_met field."""
        # If targets_met was provided during deserialization, ignore it
        # We compute it dynamically via meets_targets()
        pass

    def meets_targets(self) -> Dict[str, bool]:
        """Check if metrics meet performance targets."""
        return {
            "search_baseline": self.nodes_per_second >= 10000,
            "search_complex": self.nodes_per_second >= 5000,
            "evaluation_speed": self.evaluation_time_ms < 0.1,
            "move_generation": self.move_generation_time_ms < 0.01,
            "move_validation": self.move_validation_time_ms < 0.005,
            "style_consistency": self.style_variance_percent <= 20.0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            "nodes_per_second": self.nodes_per_second,
            "total_nodes": self.total_nodes,
            "search_time_ms": self.search_time_ms,
            "evaluation_time_ms": self.evaluation_time_ms,
            "evaluations_per_second": self.evaluations_per_second,
            "total_evaluations": self.total_evaluations,
            "move_generation_time_ms": self.move_generation_time_ms,
            "moves_generated": self.moves_generated,
            "move_validation_time_ms": self.move_validation_time_ms,
            "moves_validated": self.moves_validated,
            "memory_usage_mb": self.memory_usage_mb,
            "peak_memory_mb": self.peak_memory_mb,
            "style_variance_percent": self.style_variance_percent,
            "targets_met": self.meets_targets(),
        }


class MetricsCollector:
    """Collects and aggregates performance metrics."""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.current_metrics = PerformanceMetrics()
        self._start_times: Dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._start_times[operation] = time.perf_counter()

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration in milliseconds."""
        if operation not in self._start_times:
            return 0.0

        duration_ms = (time.perf_counter() - self._start_times[operation]) * 1000
        del self._start_times[operation]
        return duration_ms

    def record_search_metrics(self, nodes: int, time_ms: float) -> None:
        """Record search performance metrics."""
        self.current_metrics.total_nodes = nodes
        self.current_metrics.search_time_ms = time_ms
        self.current_metrics.nodes_per_second = (nodes / time_ms * 1000) if time_ms > 0 else 0

    def record_evaluation_metrics(self, evaluations: int, time_ms: float) -> None:
        """Record evaluation performance metrics."""
        self.current_metrics.total_evaluations = evaluations
        self.current_metrics.evaluation_time_ms = time_ms
        self.current_metrics.evaluations_per_second = (
            (evaluations / time_ms * 1000) if time_ms > 0 else 0
        )

    def record_move_generation_metrics(self, moves: int, time_ms: float) -> None:
        """Record move generation performance metrics."""
        self.current_metrics.moves_generated = moves
        self.current_metrics.move_generation_time_ms = time_ms

    def record_move_validation_metrics(self, moves: int, time_ms: float) -> None:
        """Record move validation performance metrics."""
        self.current_metrics.moves_validated = moves
        self.current_metrics.move_validation_time_ms = time_ms

    def record_style_variance(self, variance_percent: float) -> None:
        """Record style performance variance."""
        self.current_metrics.style_variance_percent = variance_percent

    def finalize_metrics(self) -> PerformanceMetrics:
        """Finalize and store current metrics."""
        self.metrics.append(self.current_metrics)
        finalized = self.current_metrics
        self.current_metrics = PerformanceMetrics()
        return finalized

    def get_average_metrics(self) -> PerformanceMetrics:
        """Calculate average metrics across all recorded measurements."""
        if not self.metrics:
            return PerformanceMetrics()

        total = len(self.metrics)
        return PerformanceMetrics(
            nodes_per_second=sum(m.nodes_per_second for m in self.metrics) / total,
            total_nodes=sum(m.total_nodes for m in self.metrics) // total,
            search_time_ms=sum(m.search_time_ms for m in self.metrics) / total,
            evaluation_time_ms=sum(m.evaluation_time_ms for m in self.metrics) / total,
            evaluations_per_second=sum(m.evaluations_per_second for m in self.metrics) / total,
            total_evaluations=sum(m.total_evaluations for m in self.metrics) // total,
            move_generation_time_ms=sum(m.move_generation_time_ms for m in self.metrics) / total,
            moves_generated=sum(m.moves_generated for m in self.metrics) // total,
            move_validation_time_ms=sum(m.move_validation_time_ms for m in self.metrics) / total,
            moves_validated=sum(m.moves_validated for m in self.metrics) // total,
            memory_usage_mb=sum(m.memory_usage_mb for m in self.metrics) / total,
            peak_memory_mb=sum(m.peak_memory_mb for m in self.metrics) / total,
            style_variance_percent=sum(m.style_variance_percent for m in self.metrics) / total,
        )

    def get_worst_metrics(self) -> PerformanceMetrics:
        """Get the worst performing metrics (for regression detection)."""
        if not self.metrics:
            return PerformanceMetrics()

        return min(self.metrics, key=lambda m: m.nodes_per_second)


@contextmanager
def time_operation(collector: MetricsCollector, operation: str):
    """Context manager for timing operations."""
    collector.start_timer(operation)
    try:
        yield
    finally:
        duration_ms = collector.end_timer(operation)
        # Store duration in appropriate metric based on operation name
        if "search" in operation:
            collector.current_metrics.search_time_ms = duration_ms
        elif "evaluation" in operation:
            collector.current_metrics.evaluation_time_ms = duration_ms
        elif "move_gen" in operation:
            collector.current_metrics.move_generation_time_ms = duration_ms
        elif "move_val" in operation:
            collector.current_metrics.move_validation_time_ms = duration_ms
