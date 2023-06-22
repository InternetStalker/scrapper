from __future__ import annotations

import asyncio
import pathlib
from urllib.parse import ParseResult, urljoin, urlparse, urlunparse

import aiohttp
from bs4 import BeautifulSoup

from . import System


class GithubUrl:
    "A class that provides the interface for working with Github"
    def __init__(self, url: str) -> None:
        url: ParseResult = urlparse(url)

        if url.netloc == "github.com":
            self._parse_github_url(url)

        elif url.netloc == "raw.githubusercontent.com":
            self._parse_raw_url(url)

        else:
            raise Exception(f"Invalid host: {url.netloc}")

    @property
    def author(self) -> str:
        return self._author

    @property
    def repo(self) -> str:
        return self._repo

    @property
    def path(self) -> pathlib.Path:
        return pathlib.Path(*self._path)

    @property
    def brunch(self) -> str:
        return self._brunch

    @property
    def url(self) -> str:
        return urlunparse(
            ("https",
            "github.com",
            "/".join(
                (
                    self.author,
                    self.repo,
                    "tree" if not self.__is_file else "blob",
                    self.brunch,
                    *self._path
                    )
                    ),
            "",
            "",
            "")
            )

    @property
    def raw_url(self):
        if not self._is_file:
            raise TypeError("Url doesn't destinate to a file")

        return urlunparse(
            ("https",
            "raw.githubusercontent.com",
            "/".join(
                (
                    self.author,
                    self.repo,
                    self.brunch,
                    *self.__path
                    )
                    ),
            "",
            "",
            "")
            )

    def is_file(self) -> bool:
        return self._is_file

    def is_folder(self) -> bool:
        return not self._is_file

    async def save_file(self, session: aiohttp.ClientSession) -> None:
        """Saves file from github. Checks if url is file. If not raises value error."""
        if not self.is_file():
            raise ValueError("Url argument must be url to file on github.")

        file_path = System().package_path / self.path

        async with session.get(self.raw_url) as response:
            src = await response.text()

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(src, encoding="utf-8")

    async def walk_github_tree(self, session: aiohttp.ClientSession) -> set[GithubUrl]:
        if  self.is_file():
            raise TypeError("Url should be a folder not a file")

        urls = set()

        async with session.get(self.url) as response:
            src = await response.text()

        soup = BeautifulSoup(src, "lxml")

        items = soup.find_all("a", class_="js-navigation-open Link--primary")
        for item in items:
            item_url: GithubUrl = self / item.get("href")

            if item_url.is_file(): # it's url to file
                urls.add(item_url)

            else: # url to folder
                child_urls: set[GithubUrl] = await asyncio.create_task(
                    self.walk_github_tree
                        (
                            item_url,
                            session
                        )
                    )
                urls.union(child_urls)

        return urls

    def __truediv__(self, url: str) -> GithubUrl:
        if self.is_file():
            raise Exception("Can't join to file url.")

        url = url.lstrip("/")
        parsed_url = url.split("/")

        if len(parsed_url) > 1:
            return GithubUrl("https://github.com/" + url)

        return GithubUrl(urljoin(self.url, url))

    def _parse_raw_url(self, url: ParseResult) -> None:
        self._is_file = True

        self._author, self._repo, self._brunch, *self._path = url.path.split("/")[1:]# [1:] because first is always ""

    def _parse_github_url(self, url: ParseResult) -> None:
        self._author, self._repo, *path = url.path.split("/")[1:]
        if len(path) > 0:
            if path[0] == "blob":
                self._is_file = True

            else:
                self._is_file = False

            self._brunch, *self._path = path[1:]# because first is blob or tree

        else:
            self._is_file = False
            self._brunch = "main"
            self._path = []
