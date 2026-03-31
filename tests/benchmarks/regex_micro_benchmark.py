import time
import re

# Mocking the regex use case
PATTERN = r"^[a-zA-Z0-9]+(?:['’][a-zA-Z0-9]+)*$"
COMPILED_PATTERN = re.compile(PATTERN)

def benchmark_uncompiled(parts, iterations=100000):
    start = time.time()
    for _ in range(iterations):
        for part in parts:
            if not part: continue
            re.match(PATTERN, part)
    return time.time() - start

def benchmark_compiled(parts, iterations=100000):
    start = time.perf_counter()
    for _ in range(iterations):
        for part in parts:
            if not part: continue
            COMPILED_PATTERN.match(part)
    return time.perf_counter() - start

if __name__ == "__main__":
    test_parts = ["Hello", "world", "it's", "a", "test", "123", "Shavian's", " ", "!", "..."]

    # Warm up
    benchmark_uncompiled(test_parts, 1000)
    benchmark_compiled(test_parts, 1000)

    uncompiled_time = benchmark_uncompiled(test_parts)
    compiled_time = benchmark_compiled(test_parts)

    print(f"Uncompiled: {uncompiled_time:.4f}s")
    print(f"Compiled: {compiled_time:.4f}s")
    improvement = (uncompiled_time - compiled_time) / uncompiled_time * 100
    print(f"Improvement: {improvement:.2f}%")
