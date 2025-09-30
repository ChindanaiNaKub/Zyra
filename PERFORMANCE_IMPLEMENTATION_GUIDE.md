# Performance Implementation Guide

This guide explains how to implement the performance targets defined in the OpenSpec specifications.

## 🎯 Performance Targets

| Component | Target | Implementation |
|-----------|--------|----------------|
| **Search** | 10,000 nodes/sec baseline | `search/mcts_optimized.py` |
| **Search (Complex)** | 5,000 nodes/sec | Optimized MCTS with caching |
| **Evaluation** | <0.1ms per evaluation | `eval/heuristics_optimized.py` |
| **Move Generation** | <0.01ms per position | `core/moves_optimized.py` |
| **Move Validation** | <0.005ms per move | Optimized validation |
| **Style Consistency** | <20% variance | Performance profiling |

## 🚀 Implementation Steps

### 1. **Performance Monitoring Infrastructure**

The performance monitoring system is implemented in the `performance/` module:

```python
from performance.benchmark import PerformanceBenchmark
from performance.metrics import MetricsCollector
from performance.profiler import enable_profiling, disable_profiling

# Run comprehensive benchmark
benchmark = PerformanceBenchmark()
results = benchmark.run_comprehensive_benchmark(position)

# Enable profiling for detailed analysis
enable_profiling(detailed=True)
# ... run your code ...
disable_profiling()
```

### 2. **Optimized MCTS Search**

Use the optimized MCTS implementation for 10,000+ nodes/sec:

```python
from search.mcts_optimized import OptimizedMCTSSearch

# Create optimized search engine
search_engine = OptimizedMCTSSearch(
    max_playouts=10000,
    enable_caching=True,
    enable_move_ordering=True
)

# Run search
best_move = search_engine.search(position)

# Check performance stats
stats = search_engine.get_performance_stats()
print(f"Nodes/sec: {stats['nodes_per_second']:.0f}")
```

**Key Optimizations:**
- Move ordering cache
- Node expansion caching
- Optimized UCB1 calculation
- Style-aware move selection
- Performance tracking

### 3. **Optimized Evaluation**

Use the optimized evaluation for <0.1ms per evaluation:

```python
from eval.heuristics_optimized import OptimizedEvaluation, quick_evaluate

# Create optimized evaluator
evaluator = OptimizedEvaluation(
    style_weights=style_config,
    enable_caching=True,
    enable_fast_paths=True
)

# Evaluate position
score = evaluator.evaluate(position)

# Quick evaluation for performance-critical code
score = quick_evaluate(position, style_weights)
```

**Key Optimizations:**
- LRU caching for repeated positions
- Fast lookup tables
- Optimized piece value calculations
- Cached position keys
- Fast path for common positions

### 4. **Optimized Move Generation**

Use the optimized move generator for <0.01ms per position:

```python
from core.moves_optimized import generate_moves_optimized, OptimizedMoveGenerator

# Quick move generation
moves = generate_moves_optimized(position)

# Or use the generator class for more control
generator = OptimizedMoveGenerator(enable_caching=True)
moves = generator.generate_moves(position)
```

**Key Optimizations:**
- Precomputed move offsets
- Cached legal moves
- Fast piece iteration
- Optimized pawn move generation
- Performance tracking

### 5. **Performance Regression Testing**

Run performance regression tests to ensure targets are maintained:

```bash
# Run performance tests
python performance_test.py

# Run quick test
python performance_test.py --quick

# Run regression tests
python -m pytest tests/test_performance_regression.py -v
```

### 6. **Integration with Existing Code**

To integrate the optimized components with your existing codebase:

#### **Update UCI Interface**

```python
# In interfaces/uci.py
from search.mcts_optimized import OptimizedMCTSSearch
from eval.heuristics_optimized import OptimizedEvaluation

class UCIEngine:
    def __init__(self):
        self.search_engine = OptimizedMCTSSearch()
        self.evaluator = OptimizedEvaluation()
```

#### **Update CLI Interface**

```python
# In cli/runner.py
from performance.benchmark import run_quick_benchmark

def run_performance_test():
    """Run performance test from CLI."""
    summary = run_quick_benchmark(position)
    print(f"Performance: {summary['success_rate']:.1f}% targets met")
```

## 📊 Performance Monitoring

### **Real-time Performance Tracking**

```python
from performance.metrics import MetricsCollector, time_operation

collector = MetricsCollector()

# Time operations
with time_operation(collector, "search"):
    best_move = search_engine.search(position)

# Get performance stats
stats = collector.get_average_metrics()
print(f"Search: {stats.nodes_per_second:.0f} nodes/sec")
```

### **Performance Profiling**

```python
from performance.profiler import enable_profiling, get_profiling_summary

# Enable detailed profiling
enable_profiling(detailed=True, memory=True)

# Run your code
search_engine.search(position)

# Get profiling summary
summary = get_profiling_summary()
print("Slowest functions:", summary['slowest_functions'])
```

## 🧪 Testing Performance Targets

### **Automated Testing**

```python
# Run comprehensive benchmark
from performance.benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark()
results = benchmark.run_comprehensive_benchmark(position)

# Check if targets are met
for result in results:
    if not result.passed:
        print(f"FAILED: {result.test_name} - {result.notes}")
```

### **Manual Performance Testing**

```bash
# Run the performance test script
python performance_test.py

# Expected output:
# 🚀 Chess Engine Performance Testing
# ==================================================
#
# 📊 Running comprehensive performance benchmark...
#
# 📈 Benchmark Results:
# ------------------------------
# ✅ PASS search_performance
#     Nodes/sec: 12500
# ✅ PASS evaluation_performance
#     Eval time: 0.085ms
# ✅ PASS move_generation_performance
#     Move gen time: 0.008ms
# ✅ PASS move_validation_performance
#     Move val time: 0.004ms
# ✅ PASS style_consistency
#     Style variance: 15.2%
#
# 📋 Summary:
#   Total tests: 5
#   Passed: 5
#   Failed: 0
#   Success rate: 100.0%
#
# 🎉 All performance targets met!
```

## 🔧 Configuration

### **Performance Settings**

```python
# Search optimization settings
search_config = {
    "max_playouts": 10000,
    "enable_caching": True,
    "enable_move_ordering": True,
    "exploration_constant": 1.414
}

# Evaluation optimization settings
eval_config = {
    "enable_caching": True,
    "enable_fast_paths": True,
    "cache_size": 10000
}

# Move generation optimization settings
move_config = {
    "enable_caching": True,
    "enable_fast_paths": True
}
```

### **Style Performance Consistency**

```python
# Test style consistency
from performance.benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark()
result = benchmark.benchmark_style_consistency(
    position,
    styles=["aggressive", "defensive", "experimental"]
)

# Check variance is <20%
assert result.metrics.style_variance_percent < 20.0
```

## 📈 Performance Metrics

The implementation tracks these key metrics:

- **Search Performance**: Nodes per second, search time
- **Evaluation Performance**: Evaluation time, evaluations per second
- **Move Generation**: Generation time, moves generated
- **Move Validation**: Validation time, moves validated
- **Memory Usage**: Memory consumption, cache efficiency
- **Style Consistency**: Performance variance across styles

## 🚨 Troubleshooting

### **Common Performance Issues**

1. **Search too slow**: Enable caching and move ordering
2. **Evaluation too slow**: Enable evaluation caching
3. **Move generation slow**: Enable move generation caching
4. **Memory issues**: Reduce cache sizes or disable caching
5. **Style inconsistency**: Check style weight configurations

### **Performance Debugging**

```python
# Enable detailed profiling
from performance.profiler import enable_profiling, get_profiling_summary

enable_profiling(detailed=True)

# Run your code
# ... perform operations ...

# Get detailed profiling data
summary = get_profiling_summary()
print("Function timings:", summary['timing_summary'])
print("Slowest functions:", summary['slowest_functions'])
print("Hotspots:", summary['hotspots'])
```

## 📝 Next Steps

1. **Run Performance Tests**: Execute `python performance_test.py`
2. **Integrate Optimized Components**: Update your existing code to use optimized versions
3. **Set Up Regression Testing**: Configure CI/CD to run performance regression tests
4. **Monitor Performance**: Set up continuous performance monitoring
5. **Optimize Further**: Use profiling data to identify additional optimization opportunities

The implementation provides a solid foundation for meeting all performance targets while maintaining code clarity and functionality.
