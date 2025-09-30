#!/usr/bin/env python3
"""Performance testing script for the chess engine.

This script runs comprehensive performance tests to validate that all
performance targets are met according to the specifications.
"""

import json
import sys
import time
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, ".")

from core.board import Board
from performance.benchmark import PerformanceBenchmark, run_quick_benchmark
from performance.profiler import disable_profiling, enable_profiling, get_profiling_summary
from search.mcts_optimized import OptimizedMCTSSearch


def main():
    """Run comprehensive performance tests."""
    print("🚀 Chess Engine Performance Testing")
    print("=" * 50)

    # Create test position
    position = Board()
    position.set_startpos()  # Initialize starting position
    print(f"Testing with position: {position.side_to_move} to move")

    # Enable profiling for detailed analysis
    enable_profiling(detailed=True, memory=False)

    try:
        # Run comprehensive benchmark
        print("\n📊 Running comprehensive performance benchmark...")
        benchmark = PerformanceBenchmark()
        results = benchmark.run_comprehensive_benchmark(position)

        # Display results
        print("\n📈 Benchmark Results:")
        print("-" * 30)

        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} {result.test_name}")

            if result.notes:
                for note in result.notes:
                    print(f"    {note}")

            # Show key metrics
            metrics = result.metrics
            if "search" in result.test_name:
                print(f"    Nodes/sec: {metrics.nodes_per_second:.0f}")
            elif "evaluation" in result.test_name:
                print(f"    Eval time: {metrics.evaluation_time_ms:.3f}ms")
            elif "move_gen" in result.test_name:
                print(f"    Move gen time: {metrics.move_generation_time_ms:.3f}ms")
            elif "move_val" in result.test_name:
                print(f"    Move val time: {metrics.move_validation_time_ms:.3f}ms")
            elif "style" in result.test_name:
                print(f"    Style variance: {metrics.style_variance_percent:.1f}%")

        # Get summary
        summary = benchmark.get_summary()
        print(f"\n📋 Summary:")
        print(f"  Total tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Success rate: {summary['success_rate']:.1f}%")

        # Test optimized MCTS specifically (reduced playouts for faster testing)
        print(f"\n🔍 Testing Optimized MCTS Performance...")
        max_playouts = 100  # Reduced for faster tests
        optimized_search = OptimizedMCTSSearch(max_playouts=max_playouts, seed=42)

        start_time = time.perf_counter()
        best_move = optimized_search.search(position)
        end_time = time.perf_counter()

        search_time = end_time - start_time
        nodes_per_second = max_playouts / search_time if search_time > 0 else 0

        print(f"  Search time: {search_time:.3f}s")
        print(f"  Nodes/sec: {nodes_per_second:.0f}")
        print(f"  Best move: {best_move}")
        print(f"  Target met: {'✅' if search_time < 1.0 else '❌'}  (< 1 second)")

        # Get profiling summary
        print(f"\n🔬 Performance Profiling Summary:")
        profiler_data = get_profiling_summary()

        if profiler_data.get("timing_summary"):
            print("  Function timings:")
            for func, timing in profiler_data["timing_summary"].items():
                print(
                    f"    {func}: {timing['avg_time_ms']:.3f}ms avg, {timing['call_count']} calls"
                )

        # Export results
        benchmark.export_results("performance_results.json")
        print(f"\n💾 Results exported to performance_results.json")

        # Overall result
        all_passed = all(result.passed for result in results)
        if all_passed:
            print(f"\n🎉 All performance targets met!")
            return 0
        else:
            print(f"\n⚠️  Some performance targets not met. Check results above.")
            return 1

    except Exception as e:
        print(f"\n❌ Error during performance testing: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        disable_profiling()


def run_quick_test():
    """Run a quick performance test."""
    print("🚀 Quick Performance Test")
    print("=" * 30)

    position = Board()
    summary = run_quick_benchmark(position)

    print(f"Results: {summary['passed_tests']}/{summary['total_tests']} tests passed")

    if summary["success_rate"] >= 80:
        print("✅ Performance looks good!")
        return 0
    else:
        print("⚠️  Performance issues detected")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        sys.exit(run_quick_test())
    else:
        sys.exit(main())
