from __future__ import annotations

from pathlib import Path
from urllib.parse import *
from bs4 import BeautifulSoup

import aiohttp
import asyncio

class Package:
    "A class that prepares package for unpacking files."
    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path
        self.tree_url = "https://github.com"
        self.raw_url = "https://raw.githubusercontent.com"

    async def walk_github_tree(self, url: str) -> list[str]:
        urls = []

        async with self.session.get(url) as response:
            src = await response.text()

        soup = BeautifulSoup(src, "lxml")

        items = soup.find_all("a", class_="js-navigation-open Link--primary")
        for item in items:
            item_url = urljoin(self.tree_url, item.get("href"))

            if "blob" in item_url: # it's url to file
                urls.append(item_url.replace(self.tree_url, self.raw_url).replace("blob/", ""))

            else: # url to folder
                task = self.walk_github_tree(urljoin(self.tree_url, item_url))
                child_urls = await task
                urls.extend(child_urls)

        return urls

    async def save_file(self, url: str) -> None:
        """Saves file from github. Checks if url is file. If not raises value error."""
        if "blob" in url:
            url = url.replace(self.tree_url, self.raw_url).replace("blob/", "")

        elif not self.raw_url in url:
            raise ValueError("Url argument must be url to file on github.")

        async with self.session.get(url) as response:
            src = await response.text()

        path = url.split("/")[7:]
        *path, file_name = path

        Path(self.root_path, *path, file_name).write_text(src, encoding="utf-8")



    async def __call__(self) -> None:
        """
        Calls all the methods starting with prepare.
        Prepare_ method should take no arguments.
        """
        async with aiohttp.ClientSession() as self.session:
            for name, method in Package.__dict__.items():
                if name.startswith("prepare_"):
                    task = asyncio.create_task(method(self))
                    await task

            await self.create_logs()

    async def create_logs(self) -> None:
        logs_path = self.root_path / "logs"
        logs_path.mkdir()
        service_path = self.root_path / "services"

        for service in service_path.iterdir():
            if not service == "__init__.py":
                (logs_path / service).write_text("")

        main_log = logs_path / "main.log"
        main_log.write_text("", encoding="utf-8")

    async def prepare_services(self) -> None:
        service_path = self.root_path / "services"
        service_path.mkdir()

        service_url = urljoin(self.tree_url, "/InternetStalker/scrapper/tree/main/scrapper/services")
        task = asyncio.create_task(self.walk_github_tree(service_url))
        urls = await task

        for url in urls:
            task = asyncio.create_task(self.save_file(url))
            await task

    async def prepare_modules(self) -> None:
        modules_path = self.root_path / "modules"
        modules_path.mkdir()

        modules_url = urljoin(self.tree_url, "/InternetStalker/scrapper/tree/main/scrapper/modules")
        task = asyncio.create_task(self.walk_github_tree(modules_url))
        urls = await task

        for url in urls:
            task = asyncio.create_task(self.save_file(url))
            await task

    async def prepare_webdrivers(self) -> None:
        webdrivers_path = self.root_path / "webdrivers"
        webdrivers_path.mkdir()
