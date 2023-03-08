"""Argument parser for installer of scrapper"""
from __future__ import annotations

import asyncio
import pathlib

from . import System
from .prepare_package import Package


def main():
    path_to_scrappers = pathlib.Path(input(System().phrase_table["SCRAPPERS_PATH"]))
    root_path = pathlib.Path(__file__).parent

    package = Package(root_path, path_to_scrappers)

    asyncio.run(package.prepare_package(path_to_scrappers))

if  __name__ == "__main__":
    main()
