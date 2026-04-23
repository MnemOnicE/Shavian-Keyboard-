import os
import sys
import time

# Add src and mocks to sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, os.path.join(base_dir, "src"))
sys.path.insert(0, os.path.join(base_dir, "tests/mocks"))

from lib.shavian import ShavianConverter

def benchmark(iterations=5000):
    converter = ShavianConverter()
    # A text with repeated words to benefit from caching
    text = "The quick brown fox jumps over the lazy dog. " * 10

    # Warm up
    converter.convert_sentence(text)
    converter.convert_sentence_with_ipa(text)

    print(f"Running benchmark with {iterations} iterations...")

    # Measure convert_sentence
    start_time = time.perf_counter()
    for _ in range(iterations):
        converter.convert_sentence(text)
    end_time = time.perf_counter()
    duration_sentence = end_time - start_time
    print(f"convert_sentence took {duration_sentence:.4f} seconds.")

    # Measure convert_sentence_with_ipa
    start_time = time.perf_counter()
    for _ in range(iterations):
        converter.convert_sentence_with_ipa(text)
    end_time = time.perf_counter()
    duration_ipa = end_time - start_time
    print(f"convert_sentence_with_ipa took {duration_ipa:.4f} seconds.")

    return duration_sentence, duration_ipa

if __name__ == "__main__":
    benchmark()
