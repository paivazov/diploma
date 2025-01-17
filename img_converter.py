import asyncio
import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from typing import Generator

import aiofiles
import aiohttp
import requests

from utils import count_execution_time, async_count_execution_time


class ImageConverter:
    def __init__(self, from_format: str, image_folder: str, destination_folder: str, api_url: str, workers_number: int):
        self.workers_number = workers_number
        self.image_folder = image_folder
        self.destination_folder = destination_folder
        self.from_format = from_format
        self.api_url = api_url

    def get_img_files(self) -> Generator[str, None, None]:
        """Generator that yields all img file paths in a directory."""
        for file in glob.glob(f"{self.image_folder}/*.{self.from_format}"):
            yield file

    @staticmethod
    def _get_filename(response):
        return re.findall("filename=\"(.+)\"", response.headers['Content-Disposition'])[0]

    def _convert_image_to_png(self, image_path: str) -> None:
        """Post jpg image to API, get png image response and save locally."""
        with open(image_path, "rb") as image_file:
            response = requests.post(self.api_url, files={"image": image_file})

        if response.status_code == 200:
            filename = self._get_filename(response)
            with open(f"{self.destination_folder}/{filename}", "wb") as file:
                file.write(response.content)
        else:
            print(f"Failed to convert {image_path}, status code: {response.status_code}")

    async def _async_convert_image_to_png(self, image_path: str) -> None:
        with open(image_path, "rb") as image_file:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data={"image": image_file}) as response:
                    if response.status == 200:
                        filename = self._get_filename(response)
                        async with aiofiles.open(f"{self.destination_folder}/{filename}", "wb") as file:
                            await file.write(await response.read())
                    else:
                        print(f"Failed to convert {image_path}, status code: {response.status}")

    @count_execution_time
    def single_thread_run(self):
        for file in self.get_img_files():
            self._convert_image_to_png(file)

    @count_execution_time
    def multi_thread_run(self):
        with ThreadPoolExecutor(max_workers=self.workers_number) as executor:
            for img_file in self.get_img_files():
                executor.submit(self._convert_image_to_png, img_file)

    @async_count_execution_time
    async def async_run(self):
        semaphore = asyncio.Semaphore(self.workers_number)

        async def limited_convert(image_path):
            async with semaphore:
                await self._async_convert_image_to_png(image_path)

        # Dynamically create and run tasks with a concurrency limit
        await asyncio.gather(*(limited_convert(img_file) for img_file in self.get_img_files()))

    @count_execution_time
    def multi_process_run(self):
        with Pool(processes=self.workers_number) as pool:
            pool.map(self._convert_image_to_png, self.get_img_files())


def main():
    image_folder = os.getenv("IMAGES_TO_CONVERT", "pngs")
    destination_folder = os.getenv("CONVERTED_IMAGES", "results")
    api_url = os.getenv("API_URL", "http://127.0.0.1:8000/") + "convert?output_format=jpeg"

    converter = ImageConverter("png", image_folder, destination_folder, api_url)

    print("Async run:")
    asyncio.run(converter.async_run())

    print("Multi process run:")
    converter.multi_process_run()

    print("Multi thread run:")
    converter.multi_thread_run()

    print("Single thread run:")
    converter.single_thread_run()


if __name__ == "__main__":
    main()
