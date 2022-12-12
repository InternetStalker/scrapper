from __future__ import annotations

from pathlib import Path
from urllib.parse import *
from bs4 import BeautifulSoup
from shutil import rmtree

import os
import sys
import json
import aiohttp
import asyncio

class GithubUrl:
    def __init__(self, url: str) -> None:
        url = urlparse(url)

        if url.netloc == "github.com":
            self.__parse_github_url(url)

        elif url.netloc == "raw.githubusercontent.com":
            self.__parse_raw_url(url)

        else:
            raise Exception(f"Invalid host: {url.netloc}")

    @property
    def author(self) -> str:
        return self.__author

    @property
    def repo(self) -> str:
        return self.__repo

    @property
    def path(self) -> list[str]:
        return self.__path

    @property
    def brunch(self) -> str:
        return self.__brunch

    @property
    def url(self) -> str:
        if self.__is_file:
            host = "raw.githubusercontent.com"

        else:
            host = "github.com"

        return urlunparse("https", host, self.author, self.repo, self.brunch, *self.__path)

    def is_file(self) -> bool:
        return self.__is_file

    def is_folder(self) -> bool:
        return not self.__is_file

    def __truediv__(self, url: str) -> GithubUrl:
        if self.__is_file:
            raise Exception("Can't join to file url.")

        url = url.lstrip("/")
        parsed_url = url.split("/")

        if len(parsed_url) > 1:
            return GithubUrl("https://github.com/" + url)

        else:
            return GithubUrl(self.url, url)

    def __parse_raw_url(self, url: ParseResult) -> None:
        self.__is_file = True

        self.__author, self.__repo, self.__brunch, self.__path = url.path.split("/")[1:]# [1:] because first is always ""

    def __parse_github_url(self, url: ParseResult) -> None:
        self.__author, self.__repo, *path = url.path.split("/")[1:]
        if len(path) > 0:
            if path[0] == "blob":
                self.__is_file = True

            else:
                self.__is_file = False

            self.__brunch, *self.__path = path[1:]# because first is blob or tree

        else:
            self.__brunch = "main"
            self.__path = []

class Package:
    "A class that prepares package for unpacking files."
    def __init__(self, root_path: Path, path_to_scrappers: Path) -> None:
        self.root_path = root_path
        self.path_to_scrappers = path_to_scrappers
        self.service_url = "https://github.com/InternetStalker/scrapper/tree/main/scrapper/services"
        self.modules_url = "https://github.com/InternetStalker/scrapper/tree/main/scrapper/modules"

    async def walk_github_tree(self, url: GithubUrl) -> list[str]:
        urls = []

        async with self.session.get(url.url) as response:
            src = await response.text()

        soup = BeautifulSoup(src, "lxml")

        items = soup.find_all("a", class_="js-navigation-open Link--primary")
        for item in items:
            item_url: GithubUrl = url / item.get("href")

            if item_url.is_file(): # it's url to file
                urls.append(item_url)

            else: # url to folder
                child_urls = await asyncio.create_task(
                    self.walk_github_tree(
                        item_url.url)
                    )
                urls.extend(child_urls)

        return urls

    async def save_file(self, url: GithubUrl) -> None:
        """Saves file from github. Checks if url is file. If not raises value error."""
        if not url.is_file():
            raise ValueError("Url argument must be url to file on github.")

        async with self.session.get(url.url) as response:
            src = await response.text()

        Path(self.root_path, *url.path).write_text(src, encoding="utf-8")



    async def __call__(self) -> None:
        """
        Calls all the methods starting with prepare.
        Prepare_ method should take no arguments.
        """
        async with aiohttp.ClientSession() as self.session:
            for name, method in Package.__dict__.items():
                if name.startswith("prepare_"):
                    await asyncio.create_task(method(self))

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

        urls = await asyncio.create_task(self.walk_github_tree(self.service_url))

        for url in urls:
            await asyncio.create_task(self.save_file(url))

    async def prepare_modules(self) -> None:
        modules_path = self.root_path / "modules"
        modules_path.mkdir()

        urls = await asyncio.create_task(self.walk_github_tree(self.modules_url))

        for url in urls:
            await asyncio.create_task(self.save_file(url))

    async def prepare_webdrivers(self) -> None:
        webdrivers_path = self.root_path / "webdrivers"
        webdrivers_path.mkdir()

    async def prepare_scrappers(self) -> None:
        if self.path_to_scrappers.exists():
            if not list(self.path_to_scrappers.iterdir()) == []:
                reply = input("Scrapper dirrectory contains something. Should it be cleaned? [y/n]: ")
                if reply == "y":
                    rmtree(self.path_to_scrappers)
                    self.path_to_scrappers.mkdir()
                else:
                    sys.exit(1)

        else:
            self.path_to_scrappers.mkdir()
        os.system(f"cd {self.path_to_scrappers}")
        os.system("git init")

        settings_path = self.root_path / "settings.json"
        with open(settings_path, "w", encoding="utf-8") as file:
            settings = json.loads(settings_path.read_text())
            settings["path to scrappers"] = self.path_to_scrappers
            json.dump(file, indent=4)