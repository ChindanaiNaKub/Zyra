"""Performance benchmarking framework.

This module provides comprehensive benchmarking capabilities to validate
performance targets across search, evaluation, and core operations.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from core.board import Board
from core.moves import Move, generate_moves, is_legal_move
from eval.heuristics import Evaluation, parse_style_config
from search.mcts import MCTSSearch

from .metrics import MetricsCollector, PerformanceMetrics


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""

    test_name: str
    metrics: PerformanceMetrics
    passed: bool
    target_met: Dict[str, bool]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "test_name": self.test_name,
            "metrics": self.metrics.to_dict(),
            "passed": self.passed,
            "target_met": self.target_met,
            "notes": self.notes,
        }


class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite."""

    def __init__(self):
        self.collector = MetricsCollector()
        self.results: List[BenchmarkResult] = []

    def benchmark_search_performance(
        self,
        position: Board,
        max_playouts: int = 100,  # Reduced default for faster tests
        movetime_ms: Optional[int] = None,
    ) -> BenchmarkResult:
        """Benchmark search performance against targets."""
        self.collector.start_timer("search")

        # Create search engine
        search_engine = MCTSSearch(
            max_playouts=max_playouts,
            movetime_ms=movetime_ms,
            seed=42,  # Fixed seed for reproducibility
        )

        # Run search
        start_time = time.perf_counter()
        best_move = search_engine.search(position)
        end_time = time.perf_counter()

        search_time_ms = (end_time - start_time) * 1000
        nodes_per_second = (max_playouts / search_time_ms * 1000) if search_time_ms > 0 else 0

        # Record metrics
        self.collector.record_search_metrics(max_playouts, search_time_ms)
        metrics = self.collector.finalize_metrics()

        # Check targets
        target_met = metrics.meets_targets()
        passed = target_met["search_baseline"] and target_met["search_complex"]

        notes = []
        if not target_met["search_baseline"]:
            notes.append(f"Failed baseline target: {nodes_per_second:.0f} < 10,000 nodes/sec")
        if not target_met["search_complex"]:
            notes.append(f"Failed complex target: {nodes_per_second:.0f} < 5,000 nodes/sec")

        result = BenchmarkResult(
            test_name="search_performance",
            metrics=metrics,
            passed=passed,
            target_met=target_met,
            notes=notes,
        )

        self.results.append(result)
        return result

    def benchmark_evaluation_performance(
        self, position: Board, num_evaluations: int = 1000
    ) -> BenchmarkResult:
        """Benchmark evaluation performance against targets."""
        evaluator = Evaluation()

        self.collector.start_timer("evaluation")
        start_time = time.perf_counter()

        # Run multiple evaluations
        for _ in range(num_evaluations):
            score = evaluator.evaluate(position)

        end_time = time.perf_counter()
        evaluation_time_ms = (end_time - start_time) * 1000
        per_evaluation_time_ms = evaluation_time_ms / num_evaluations
        evaluations_per_second = (
            (num_evaluations / evaluation_time_ms * 1000) if evaluation_time_ms > 0 else 0
        )

        # Record metrics (per-operation time)
        self.collector.record_evaluation_metrics(num_evaluations, per_evaluation_time_ms)
        metrics = self.collector.finalize_metrics()

        # Check targets
        target_met = metrics.meets_targets()
        passed = target_met["evaluation_speed"]

        notes = []
        if not target_met["evaluation_speed"]:
            notes.append(
                f"Failed evaluation target: {per_evaluation_time_ms:.3f}ms > 0.1ms per evaluation"
            )

        result = BenchmarkResult(
            test_name="evaluation_performance",
            metrics=metrics,
            passed=passed,
            target_met=target_met,
            notes=notes,
        )

        self.results.append(result)
        return result

    def benchmark_move_generation_performance(
        self, position: Board, num_iterations: int = 1000
    ) -> BenchmarkResult:
        """Benchmark move generation performance against targets."""
        self.collector.start_timer("move_generation")
        start_time = time.perf_counter()

        total_moves = 0
        for _ in range(num_iterations):
            moves = generate_moves(position)
            total_moves += len(moves)

        end_time = time.perf_counter()
        generation_time_ms = (end_time - start_time) * 1000
        per_generation_time_ms = generation_time_ms / num_iterations

        # Record metrics (per-operation time)
        self.collector.record_move_generation_metrics(total_moves, per_generation_time_ms)
        metrics = self.collector.finalize_metrics()

        # Check targets
        target_met = metrics.meets_targets()
        passed = target_met["move_generation"]

        notes = []
        if not target_met["move_generation"]:
            notes.append(f"Failed move generation target: {per_generation_time_ms:.3f}ms > 0.01ms")

        result = BenchmarkResult(
            test_name="move_generation_performance",
            metrics=metrics,
            passed=passed,
            target_met=target_met,
            notes=notes,
        )

        self.results.append(result)
        return result

    def benchmark_move_validation_performance(
        self, position: Board, num_iterations: int = 1000
    ) -> BenchmarkResult:
        """Benchmark move validation performance against targets."""
        # Generate some moves to validate
        moves = generate_moves(position)
        if not moves:
            # Create dummy moves for testing
            moves = [Move(0, 1), Move(1, 2), Move(2, 3)]

        self.collector.start_timer("move_validation")
        start_time = time.perf_counter()

        total_validations = 0
        for _ in range(num_iterations):
            for move in moves:
                is_legal_move(position, move)
                total_validations += 1

        end_time = time.perf_counter()
        validation_time_ms = (end_time - start_time) * 1000
        per_validation_time_ms = (
            validation_time_ms / total_validations if total_validations > 0 else 0
        )

        # Record metrics (per-operation time)
        self.collector.record_move_validation_metrics(total_validations, per_validation_time_ms)
        metrics = self.collector.finalize_metrics()

        # Check targets
        target_met = metrics.meets_targets()
        passed = target_met["move_validation"]

        notes = []
        if not target_met["move_validation"]:
            notes.append(f"Failed move validation target: {per_validation_time_ms:.3f}ms > 0.005ms")

        result = BenchmarkResult(
            test_name="move_validation_performance",
            metrics=metrics,
            passed=passed,
            target_met=target_met,
            notes=notes,
        )

        self.results.append(result)
        return result

    def benchmark_style_consistency(
        self, position: Board, styles: List[str] = ["aggressive", "defensive", "experimental"]
    ) -> BenchmarkResult:
        """Benchmark style performance consistency."""
        style_metrics = []

        for style in styles:
            # Parse style configuration
            style_config = parse_style_config(style)
            evaluator = Evaluation(style_weights=style_config)

            # Time evaluation
            start_time = time.perf_counter()
            for _ in range(100):  # Multiple evaluations for consistency
                score = evaluator.evaluate(position)
            end_time = time.perf_counter()

            evaluation_time_ms = (end_time - start_time) * 1000
            style_metrics.append(evaluation_time_ms)

        # Calculate variance
        if len(style_metrics) > 1:
            avg_time = sum(style_metrics) / len(style_metrics)
            variance = sum((t - avg_time) ** 2 for t in style_metrics) / len(style_metrics)
            variance_percent = (variance**0.5 / avg_time * 100) if avg_time > 0 else 0
        else:
            variance_percent = 0

        # Record metrics
        self.collector.record_style_variance(variance_percent)
        metrics = self.collector.finalize_metrics()

        # Check targets
        target_met = metrics.meets_targets()
        passed = target_met["style_consistency"]

        notes = []
        if not target_met["style_consistency"]:
            notes.append(f"Failed style consistency target: {variance_percent:.1f}% > 20% variance")

        result = BenchmarkResult(
            test_name="style_consistency",
            metrics=metrics,
            passed=passed,
            target_met=target_met,
            notes=notes,
        )

        self.results.append(result)
        return result

    def run_comprehensive_benchmark(self, position: Board) -> List[BenchmarkResult]:
        """Run all performance benchmarks."""
        print("Running comprehensive performance benchmark...")

        # Clear previous results
        self.results.clear()

        # Run all benchmarks
        print("  - Benchmarking search performance...")
        self.benchmark_search_performance(position)

        print("  - Benchmarking evaluation performance...")
        self.benchmark_evaluation_performance(position)

        print("  - Benchmarking move generation performance...")
        self.benchmark_move_generation_performance(position)

        print("  - Benchmarking move validation performance...")
        self.benchmark_move_validation_performance(position)

        print("  - Benchmarking style consistency...")
        self.benchmark_style_consistency(position)

        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all benchmark results."""
        if not self.results:
            return {"error": "No benchmark results available"}

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": [r.to_dict() for r in self.results],
        }

        return summary

    def export_results(self, filename: str) -> None:
        """Export benchmark results to file."""
        import json

        with open(filename, "w") as f:
            json.dump(self.get_summary(), f, indent=2)

        print(f"Benchmark results exported to {filename}")


def run_quick_benchmark(position: Board) -> Dict[str, Any]:
    """Run a quick performance benchmark."""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_comprehensive_benchmark(position)
    return benchmark.get_summary()
