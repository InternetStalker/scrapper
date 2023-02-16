


import asyncio
import pathlib

import aiohttp
import requests

from installer.tests.test_url import blob_url, folder_url, raw_url

from ..scrapper.prepare_package import Package
from ..scrapper.url import GithubUrl


def test_path_to_scrappers(tmp_path: pathlib.Path):
    root_path = tmp_path / "package"
    root_path.mkdir(exist_ok=True, parents=True)
    scrapper_path = tmp_path / "sc"
    scrapper_path.mkdir(exist_ok=True, parents=True)
    assert Package(root_path, scrapper_path).path_to_scrappers == scrapper_path


def test_save_file(tmp_path: pathlib.Path):
    root_path = tmp_path / "package"
    root_path.mkdir(exist_ok=True, parents=True)
    async def save():
        async with aiohttp.ClientSession() as session:
            return await GithubUrl(blob_url).save_file(session)

    asyncio.run(save())
    file_path = root_path / "folder1" / "file2"
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == requests.get(raw_url).text
