"""Argument parser for installer of scrapper"""
from __future__ import annotations

import asyncio
import pathlib

import aiohttp

from . import System
from .prepare_package import Package


async def prepare_package(path_to_scrappers: pathlib.Path):
    "Manages all the logic of preparing"
    package = Package(System().package_path, path_to_scrappers)
    async with aiohttp.ClientSession() as session:
        await asyncio.create_task(package.prepare_package(session))
        await asyncio.create_task(package.prepare_webdrivers(session))
        await asyncio.create_task(package.prepare_scrappers())

        await package.create_logs()


def main():
    path_to_scrappers = pathlib.Path(input(System().phrase_table["SCRAPPERS_PATH"]))

    asyncio.run(prepare_package(path_to_scrappers))

if  __name__ == "__main__":
    main()
