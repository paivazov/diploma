import re
import glob
from typing import Generator
from concurrent.futures import ThreadPoolExecutor

import psutil
import requests

from utils import count_execution_time


class ImageConverter:
    def __init__(self, from_format: str, image_folder: str, destination_folder: str, api_url: str):
        self.image_folder = image_folder
        self.destination_folder = destination_folder
        self.from_format = from_format
        self.api_url = api_url

    def get_img_files(self) -> Generator[str, None, None]:
        """Generator that yields all img file paths in a directory."""
        for file in glob.glob(f"{self.image_folder}/*.{self.from_format}"):
            yield file

    def convert_image_to_png(self, image_path: str) -> None:
        """Post jpg image to API, get png image response and save locally."""
        with open(image_path, "rb") as image_file:
            response = requests.post(self.api_url, files={"image": image_file})

        if response.status_code == 200:
            filename = re.findall("filename=\"(.+)\"", response.headers['content-disposition'])[0]
            with open(f"{self.destination_folder}/{filename}", "wb") as file:
                file.write(response.content)
        else:
            print(f"Failed to convert {image_path}, status code: {response.status_code}")

    @staticmethod
    def get_max_workers():
        """Returns the number of workers based on available memory."""
        mem = psutil.virtual_memory()

        # Estimate the memory usage per thread (this is just my assumption)
        mem_per_thread = 100 * 1024 ** 2  # 100 MB

        # Calculate the number of threads that we can run based on available memory
        max_workers = mem.available // mem_per_thread

        # Ensure at least one worker
        return max(1, max_workers)

    @count_execution_time
    def multi_thread_run(self):
        max_workers = self.get_max_workers()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for img_file in self.get_img_files():
                executor.submit(self.convert_image_to_png, img_file)

    @count_execution_time
    def single_thread_run(self):
        for file in self.get_img_files():
            self.convert_image_to_png(file)


def main():
    api_url = "http://146.190.177.222:8000/convert?output_format=jpeg"
    image_folder = "/Users/paivazov/Documents/images/png"
    destination_folder = "/Users/paivazov/Documents/images/converted_images"

    converter = ImageConverter("png", image_folder, destination_folder, api_url)
    print("Multi thread run:")
    converter.multi_thread_run()
    print("Single thread run:")
    converter.single_thread_run()


if __name__ == "__main__":
    main()
