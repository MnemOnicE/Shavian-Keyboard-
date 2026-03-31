import timeit

class MockSegment:
    def __init__(self, text):
        self.text = text

def generate_segments(num_segments):
    return (MockSegment(f"word{i}") for i in range(num_segments))

def concat_loop(segments):
    full_text = ""
    for segment in segments:
        full_text += segment.text + " "
    return full_text.strip()

def concat_join_list(segments):
    return " ".join([segment.text for segment in segments]).strip()

if __name__ == "__main__":
    num_segments = 1000
    num_iterations = 10000

    segments = list(generate_segments(num_segments))

    time_loop = timeit.timeit(lambda: concat_loop(segments), number=num_iterations)
    time_join_list = timeit.timeit(lambda: concat_join_list(segments), number=num_iterations)

    print(f"Loop concatenation: {time_loop:.4f} seconds")
    print(f"Join (list comp):   {time_join_list:.4f} seconds")
