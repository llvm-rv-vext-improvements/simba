import time
from contextlib import contextmanager

from simba.log import loggy


@contextmanager
def timer():
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    loggy.info(f"Elapsed time: {end - start:.2f} seconds")
