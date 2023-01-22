import asyncio
import pathlib
import unittest

import aiohttp
from prepare_package import GithubUrl, Package

tmp_path = pathlib.Path("./tmp/")

class GithubUrlTest(unittest.TestCase):
    blob_url = "https://github.com/InternetStalker/scrapper/blob/installer-test/folder1/file2"
    folder_url = "https://github.com/InternetStalker/scrapper/tree/installer-test/folder1"
    raw_url = "https://raw.githubusercontent.com/InternetStalker/scrapper/installer-test/folder1/file2"
    root_url = "https://github.com/InternetStalker/scrapper"
    def test_author(self):
        assert GithubUrl(self.blob_url).author == "InternetStalker"
        assert GithubUrl(self.folder_url).author == "InternetStalker"
        assert GithubUrl(self.raw_url).author == "InternetStalker"
        assert GithubUrl(self.root_url).author == "InternetStalker"

    def test_repo(self):
        assert GithubUrl(self.blob_url).repo == "scrapper"
        assert GithubUrl(self.folder_url).repo == "scrapper"
        assert GithubUrl(self.raw_url).repo == "scrapper"
        assert GithubUrl(self.root_url).repo == "scrapper"

    def test_path(self):
        assert GithubUrl(self.blob_url).path == pathlib.Path("folder1/file2")
        assert GithubUrl(self.folder_url).path == pathlib.Path("folder1")
        assert GithubUrl(self.raw_url).path == pathlib.Path("folder1/file2")
        assert GithubUrl(self.root_url).path == pathlib.Path("")

    def test_brunch(self):
        assert GithubUrl(self.blob_url).brunch == "installer-test"
        assert GithubUrl(self.folder_url).brunch == "installer-test"
        assert GithubUrl(self.raw_url).brunch == "installer-test"
        assert GithubUrl(self.root_url).brunch == "main"

    def test_url(self):
        assert GithubUrl(self.blob_url).url == self.blob_url
        assert GithubUrl(self.folder_url).url == self.folder_url
        assert GithubUrl(self.root_url).url == "https://github.com/InternetStalker/scrapper/tree/main"

    def test_is_file(self):
        assert GithubUrl(self.blob_url).is_file()
        assert GithubUrl(self.raw_url).is_file()
        assert not GithubUrl(self.folder_url).is_file()
        assert not GithubUrl(self.root_url).is_file()

    def test_is_folder(self):
        assert GithubUrl(self.root_url).is_folder()
        assert GithubUrl(self.folder_url).is_folder()
        assert not GithubUrl(self.blob_url).is_folder()
        assert not GithubUrl(self.raw_url).is_folder()

class PackageTest(unittest.TestCase):
    def test_root_path(self):
        root_path = tmp_path / "package"
        root_path.mkdir(exist_ok=True, parents=True)
        scrapper_path = tmp_path / "sc"
        scrapper_path.mkdir(exist_ok=True, parents=True)
        assert Package(root_path, scrapper_path).root_path == root_path

    def test_path_to_scrappers(self):
        root_path = tmp_path / "package"
        root_path.mkdir(exist_ok=True, parents=True)
        scrapper_path = tmp_path / "sc"
        scrapper_path.mkdir(exist_ok=True, parents=True)
        assert Package(root_path, scrapper_path).path_to_scrappers == scrapper_path

    def test_walk_github_tree(self):
        root_path = tmp_path / "package"
        root_path.mkdir(exist_ok=True, parents=True)
        scrapper_path = tmp_path / "sc"
        scrapper_path.mkdir(exist_ok=True, parents=True)
        package = Package(root_path, scrapper_path)
        async def walk():
            async with aiohttp.ClientSession() as session:
                res = await package.walk_github_tree(GithubUrl(GithubUrlTest.folder_url), session)
                return res
        assert [url.url for url in asyncio.run(walk())] == [
            GithubUrlTest.blob_url
        ]
