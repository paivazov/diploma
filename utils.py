import time


def count_execution_time(func):
    def _wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        finish_time = time.perf_counter()
        print("Execution of function ended. Duration:", finish_time - start_time)

    return _wrapper
