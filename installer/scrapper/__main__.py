"""Argument parser for installer of scrapper"""
from __future__ import annotations

from .prepare_package import Package

import asyncio
import pathlib

def main():
    root_path = pathlib.Path(__file__).parent
    asyncio.run(Package(root_path)())

if  __name__ == "__main__":
    main()
