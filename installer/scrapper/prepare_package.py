from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
from shutil import rmtree

import aiohttp

from . import System
from .url import GithubUrl
from .webdrivers import ChromeWebdriver


class Package:
    "A class that prepares package for unpacking files."
    def __init__(self, package_path: pathlib.Path, path_to_scrappers: pathlib.Path) -> None:
        self._package_path = package_path
        self._path_to_scrappers = path_to_scrappers
        self._source_url = GithubUrl("https://github.com/InternetStalker/scrapper/tree/main/scrapper")

    @property
    def package_path(self) -> pathlib.Path:
        "Path where package is installed"
        return self._package_path

    @property
    def path_to_scrappers(self) -> pathlib.Path:
        "Path to the folder where scrappers are"
        return self._path_to_scrappers

    def create_logs(self) -> None:
        "Create logs"
        logs_path = self.package_path / "logs"
        logs_path.mkdir()
        service_path = self.package_path / "services"

        for service in service_path.iterdir():
            if not service == "__init__.py":
                (logs_path / service).write_text("")

        main_log = logs_path / "main.log"
        main_log.write_text("", encoding="utf-8")

    async def prepare_files(self, session: aiohttp.ClientSession) -> None:
        "Download files from the Github"
        urls = await asyncio.create_task(self._source_url.walk_github_tree(session))

        for url in urls:
            await asyncio.create_task(url.save_file(session))

    async def prepare_webdrivers(self, session: aiohttp.ClientSession) -> None:
        "Download webdrivers"
        webdrivers_path = self.package_path / "webdrivers"
        webdrivers_path.mkdir()

        await asyncio.create_task(ChromeWebdriver().install(session, webdrivers_path))

    async def prepare_scrappers(self) -> None:
        "Creates place for scrappers"
        if self.path_to_scrappers.exists():
            if list(self.path_to_scrappers.iterdir()):
                reply = input(System().phrase_table["CRAPPER_CONTAINS"])
                if reply == "y":
                    rmtree(self.path_to_scrappers)
                    self.path_to_scrappers.mkdir()
                else:
                    sys.exit(1)

        else:
            self.path_to_scrappers.mkdir()
        os.system(f"cd {self.path_to_scrappers} && git init")

        settings_path = self.package_path / "settings.json"
        while settings_path.read_text() == "":
            await asyncio.sleep(0.1)
        settings = json.loads(settings_path.read_text())
        settings["path to scrappers"] = str(self.path_to_scrappers)
        settings_path.write_text(json.dumps(settings, indent=4))

    async def prepare_package(self):
        "Manages all the installing logic"

        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(self.prepare_files(session))
            await asyncio.create_task(self.prepare_webdrivers(session))
            await asyncio.create_task(self.prepare_scrappers())

        self.create_logs()
