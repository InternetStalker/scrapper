"""Argument parser for installer of scrapper"""
from __future__ import annotations

from .prepare_package import Package

import asyncio
import pathlib

def main():
    root_path = pathlib.Path(__file__).parent
    path_to_scrappers = pathlib.Path(input("Enter path to folder where your scrapper will be: "))

    asyncio.run(Package(root_path, path_to_scrappers)())

if  __name__ == "__main__":
    main()
