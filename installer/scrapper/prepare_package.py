from __future__ import annotations

import os
import sys
import json
import asyncio

from pathlib import Path
from shutil import rmtree
from urllib.parse import urlparse, urlunparse, ParseResult, urljoin

import aiohttp

from bs4 import BeautifulSoup

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
    def path(self) -> Path:
        return Path(*self.__path[1:])

    @property
    def brunch(self) -> str:
        return self.__brunch

    @property
    def url(self) -> str:
        if self.__is_file:
            host = "raw.githubusercontent.com"

        else:
            host = "github.com"
        return urlunparse(
            ("https",
            host,
            "/".join((self.author, self.repo, ("tree" if not self.__is_file else ""), self.brunch, *self.__path)),
            "",
            "",
            "")
            )

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

        return GithubUrl(urljoin(self.url, url))

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
        self.__root_path = root_path
        self.__path_to_scrappers = path_to_scrappers
        self.__source_url = GithubUrl("https://github.com/InternetStalker/scrapper/tree/main/scrapper")

    @property
    def root_path(self) -> Path:
        return self.__root_path

    @property
    def path_to_scrappers(self) -> Path:
        return self.__path_to_scrappers

    async def walk_github_tree(self, url: GithubUrl, session: aiohttp.ClientSession) -> list[str]:
        urls = []

        async with session.get(url.url) as response:
            src = await response.text()

        soup = BeautifulSoup(src, "lxml")

        items = soup.find_all("a", class_="js-navigation-open Link--primary")
        for item in items:
            item_url: GithubUrl = url / item.get("href")

            if item_url.is_file(): # it's url to file
                urls.append(item_url)

            else: # url to folder
                child_urls = await asyncio.create_task(
                    self.walk_github_tree
                        (
                            item_url,
                            session
                        )
                    )
                urls.extend(child_urls)

        return urls

    async def save_file(self, url: GithubUrl, session: aiohttp.ClientSession) -> None:
        """Saves file from github. Checks if url is file. If not raises value error."""
        if not url.is_file():
            raise ValueError("Url argument must be url to file on github.")

        file_path = Path(self.root_path, url.path)

        async with session.get(url.url) as response:
            src = await response.text()

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(src, encoding="utf-8")



    async def __call__(self) -> None:
        """
        Calls all the methods starting with prepare.
        Prepare_ method should take no arguments.
        """
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(self.prepare_package(session))
            await asyncio.create_task(self.prepare_webdrivers(session))
            await asyncio.create_task(self.prepare_scrappers())

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

    async def prepare_package(self, session: aiohttp.ClientSession) -> None:
        urls = await asyncio.create_task(self.walk_github_tree(self.__source_url, session))

        for url in urls:
            await asyncio.create_task(self.save_file(url, session))

    async def prepare_webdrivers(self, session) -> None:
        webdrivers_path = self.root_path / "webdrivers"
        webdrivers_path.mkdir()

    async def prepare_scrappers(self) -> None:
        if self.path_to_scrappers.exists():
            if list(self.path_to_scrappers.iterdir()):
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
        st = settings_path.read_text()
        while st == "":
            await asyncio.sleep(0.1)
            st = settings_path.read_text()
        settings = json.loads(st)
        settings["path to scrappers"] = str(self.path_to_scrappers)
        settings_path.write_text(json.dumps(settings, indent=4))
