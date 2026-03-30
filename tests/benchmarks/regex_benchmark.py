import time
import sys
import os
import re

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from lib.shavian import ShavianConverter

def benchmark(iterations=1000):
    converter = ShavianConverter()
    text = "The quick brown fox jumps over the lazy dog. It's a beautiful day, isn't it? 'Shavian' is a phonetic alphabet."

    start_time = time.time()
    for _ in range(iterations):
        converter.convert_sentence(text)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Benchmark took {duration:.4f} seconds for {iterations} iterations.")
    return duration

if __name__ == "__main__":
    benchmark()
