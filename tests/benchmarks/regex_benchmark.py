import os
# import re
import sys
import time

# Add src and mocks to sys.path relative to this file
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, os.path.join(base_dir, "src"))
sys.path.insert(0, os.path.join(base_dir, "tests/mocks"))

from lib.shavian import ShavianConverter  # noqa: E402


def benchmark(iterations=1000):
    converter = ShavianConverter()
    text = "The quick brown fox jumps over the lazy dog. It's a beautiful day, isn't it? 'Shavian' is a phonetic alphabet."  # noqa: E501

    start_time = time.perf_counter()
    for _ in range(iterations):
        converter.convert_sentence(text)
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"Benchmark took {duration:.4f} seconds for {iterations} iterations.")  # noqa: E501
    return duration


if __name__ == "__main__":
    benchmark()
