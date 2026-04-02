import timeit
import collections
import numpy as np
import os

def setup_buffers():
    # Simulate 10 frames of 480 float32 samples (30ms at 16kHz)
    frames = [np.random.randn(480).astype(np.float32) for _ in range(10)]
    pre_trigger_buffer = collections.deque(frames, maxlen=10)
    speech_buffer = []
    return pre_trigger_buffer, speech_buffer

def benchmark_loop():
    pre_trigger_buffer, speech_buffer = setup_buffers()
    for f in pre_trigger_buffer:
        speech_buffer.append(f)

def benchmark_extend():
    pre_trigger_buffer, speech_buffer = setup_buffers()
    speech_buffer.extend(pre_trigger_buffer)

if __name__ == "__main__":
    print("Running benchmarks...")

    # We want to measure just the operation, not the setup, but setup is fast enough
    # Let's decouple setup to isolate the exact operation

    setup_code = '''
import collections
import numpy as np
frames = [np.random.randn(480).astype(np.float32) for _ in range(10)]
'''

    loop_code = '''
pre_trigger_buffer = collections.deque(frames, maxlen=10)
speech_buffer = []
for f in pre_trigger_buffer:
    speech_buffer.append(f)
'''

    extend_code = '''
pre_trigger_buffer = collections.deque(frames, maxlen=10)
speech_buffer = []
speech_buffer.extend(pre_trigger_buffer)
'''

    iterations = 1_000_000

    loop_time = timeit.timeit(stmt=loop_code, setup=setup_code, number=iterations)
    print(f"Loop time: {loop_time:.4f}s")

    extend_time = timeit.timeit(stmt=extend_code, setup=setup_code, number=iterations)
    print(f"Extend time: {extend_time:.4f}s")

    improvement_pct = ((loop_time - extend_time) / loop_time) * 100
    speedup = loop_time / extend_time

    print(f"Improvement: {improvement_pct:.2f}% ({speedup:.2f}x faster)")

    # Write results to markdown
    md_path = os.path.join(os.path.dirname(__file__), "vad_extend_results.md")

    with open(md_path, "w") as f:
        f.write("# VAD Buffer Transfer Optimization Benchmark\n\n")
        f.write("This benchmark compares the performance of transferring frames from a `collections.deque` to a `list`.\n\n")
        f.write("## Methodology\n")
        f.write(f"- Iterations: {iterations:,}\n")
        f.write("- Data: 10 NumPy arrays of 480 `float32` elements (simulating 300ms of 16kHz audio).\n\n")
        f.write("## Results\n\n")
        f.write("| Method | Time (seconds) |\n")
        f.write("|--------|----------------|\n")
        f.write(f"| `for` loop with `append` (Baseline) | {loop_time:.4f} |\n")
        f.write(f"| `list.extend()` (Optimized) | {extend_time:.4f} |\n\n")
        f.write("## Conclusion\n\n")
        f.write(f"Using `extend()` is **{improvement_pct:.2f}% faster** ({speedup:.2f}x speedup) than iterating and appending.\n")

    print(f"Results written to {md_path}")
