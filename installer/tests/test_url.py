import asyncio
import pathlib

import aiohttp
import requests

from ..scrapper.url import GithubUrl

tmp_path = pathlib.Path("./tmp/")

blob_url = "https://github.com/InternetStalker/scrapper/blob/installer-test/folder1/file2"
folder_url = "https://github.com/InternetStalker/scrapper/tree/installer-test/folder1"
raw_url = "https://raw.githubusercontent.com/InternetStalker/scrapper/installer-test/folder1/file2"
root_url = "https://github.com/InternetStalker/scrapper"

def test_author():
    assert GithubUrl(blob_url).author == "InternetStalker"
    assert GithubUrl(folder_url).author == "InternetStalker"
    assert GithubUrl(raw_url).author == "InternetStalker"
    assert GithubUrl(root_url).author == "InternetStalker"

def test_repo():
    assert GithubUrl(blob_url).repo == "scrapper"
    assert GithubUrl(folder_url).repo == "scrapper"
    assert GithubUrl(raw_url).repo == "scrapper"
    assert GithubUrl(root_url).repo == "scrapper"

def test_path():
    assert GithubUrl(blob_url).path == pathlib.Path("folder1/file2")
    assert GithubUrl(folder_url).path == pathlib.Path("folder1")
    assert GithubUrl(raw_url).path == pathlib.Path("folder1/file2")
    assert GithubUrl(root_url).path == pathlib.Path("")

def test_brunch():
    assert GithubUrl(blob_url).brunch == "installer-test"
    assert GithubUrl(folder_url).brunch == "installer-test"
    assert GithubUrl(raw_url).brunch == "installer-test"
    assert GithubUrl(root_url).brunch == "main"

def test_url():
    assert GithubUrl(blob_url).url == blob_url
    assert GithubUrl(folder_url).url == folder_url
    assert GithubUrl(root_url).url == "https://github.com/InternetStalker/scrapper/tree/main"

def test_is_file():
    assert GithubUrl(blob_url).is_file()
    assert GithubUrl(raw_url).is_file()
    assert not GithubUrl(folder_url).is_file()
    assert not GithubUrl(root_url).is_file()

def test_is_folder():
    assert GithubUrl(root_url).is_folder()
    assert GithubUrl(folder_url).is_folder()
    assert not GithubUrl(blob_url).is_folder()
    assert not GithubUrl(raw_url).is_folder()

def test_walk_github_tree():
    async def walk():
        async with aiohttp.ClientSession() as session:
            res = await GithubUrl(folder_url).walk_github_tree(session)
            return res
    assert {url.url for url in asyncio.run(walk())} == {
        blob_url
    }


async def test_save_file(tmp_path: pathlib.Path):
    root_path = tmp_path / "package"
    root_path.mkdir(exist_ok=True, parents=True)
    async with aiohttp.ClientSession() as session:
        await GithubUrl(blob_url).save_file(session)
    file_path = root_path / "folder1" / "file2"
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == requests.get(raw_url).text
