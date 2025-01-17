import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

from utils import count_execution_time, async_count_execution_time, get_max_workers


class FibonacciCounter:
    def __init__(self, final_fibonacci_number: int):
        self.final_fibonacci_number = final_fibonacci_number
        self.max_workers = get_max_workers()

    @property
    def _tasks_number(self) -> list:
        return list(range(1, self.final_fibonacci_number + 1))

    def count_fibonacci(self, number):
        if number in (1, 2):
            return 1
        return self.count_fibonacci(number - 1) + self.count_fibonacci(number - 2)

    @count_execution_time
    def single_thread_run(self):
        tasks = self._tasks_number
        answers = []
        for number in tasks:
            answers.append(self.count_fibonacci(number))
        print(*answers)

    @count_execution_time
    def multi_thread_run(self):
        tasks = self._tasks_number
        answers = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for task in tasks:
                future = executor.submit(self.count_fibonacci, task)
                answers.append(future.result())
        print(*answers)

    @async_count_execution_time
    async def async_run(self):
        tasks = self._tasks_number

        async def async_fib(number):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.count_fibonacci, number)

        coroutines = [async_fib(task) for task in tasks]
        answers = await asyncio.gather(*coroutines)
        print(*answers)

    @count_execution_time
    def multi_process_run(self):
        tasks = self._tasks_number
        with Pool(processes=self.max_workers) as pool:
            answers = pool.map(self.count_fibonacci, tasks)
        print(*answers)


def main():
    counter = FibonacciCounter(40)

    print("Async run:")
    asyncio.run(counter.async_run())

    print("Multi process run:")
    counter.multi_process_run()

    print("Multi thread run:")
    counter.multi_thread_run()

    print("Single thread run:")
    counter.single_thread_run()


if __name__ == '__main__':
    main()
