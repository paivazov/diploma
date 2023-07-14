from concurrent.futures import ThreadPoolExecutor

from img_converter import ImageConverter
from utils import count_execution_time


class FibonacciCounter:
    def __init__(self, final_fibonacci_number: int):
        self.final_fibonacci_number = final_fibonacci_number
        self.max_workers = ImageConverter.get_max_workers()

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
        with ThreadPoolExecutor(max_workers=20) as executor:
            for task in tasks:
                future = executor.submit(self.count_fibonacci, task)
                answers.append(future.result())
        print(*answers)


def main():
    counter = FibonacciCounter(40)
    print("Multi thread run:")
    counter.multi_thread_run()
    print("Single thread run:")
    counter.single_thread_run()


if __name__ == '__main__':
    main()
