import time
from datetime import timedelta


class Stopwatch:
    def __init__(self):
        self.duration = timedelta()

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        self.duration = timedelta(seconds=self.end - self.start)
