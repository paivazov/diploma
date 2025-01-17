import time

import psutil


def count_execution_time(func):
    def _wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        finish_time = time.perf_counter()
        print("Execution of function ended. Duration:", finish_time - start_time)

    return _wrapper


def async_count_execution_time(func):
    async def _wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        await func(*args, **kwargs)
        finish_time = time.perf_counter()
        print("Execution of async function ended. Duration:", finish_time - start_time)

    return _wrapper


def get_max_workers():
    """Returns the number of workers based on available memory."""
    mem = psutil.virtual_memory()

    # Estimate the memory usage per thread (this is just my assumption)
    mem_per_thread = 100 * 1024 ** 2  # 100 MB

    # Calculate the number of threads that we can run based on available memory
    max_workers = mem.available // mem_per_thread

    # Ensure at least one worker
    return max(1, max_workers)
