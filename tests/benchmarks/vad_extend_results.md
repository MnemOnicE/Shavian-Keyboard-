# VAD Buffer Transfer Optimization Benchmark

This benchmark compares the performance of transferring frames from a `collections.deque` to a `list`.

## Methodology
- Iterations: 1,000,000
- Data: 10 NumPy arrays of 480 `float32` elements (simulating 300ms of 16kHz audio).

## Results

| Method | Time (seconds) |
|--------|----------------|
| `for` loop with `append` (Baseline) | 1.2025 |
| `list.extend()` (Optimized) | 0.9662 |

## Conclusion

Using `extend()` is **19.65% faster** (1.24x speedup) than iterating and appending.
