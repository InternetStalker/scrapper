from __future__ import annotations

import os
import pathlib
import platform
from abc import ABC, abstractmethod, abstractproperty

import aiohttp
from bs4 import BeautifulSoup, Tag


class AbstractBrowser(ABC):
    @abstractproperty
    def is_installed(self) -> bool:
        "Return if the browser is installed"

    @abstractproperty
    def version(self) -> str:
        "Version of the installed browser"

class BaseBrowser(AbstractBrowser):
    def __init__(self) -> None:
        self._is_installed = self._get_is_installed()
        self._version = self._get_version()

    @property
    def is_installed(self) -> bool:
        "Return if the browser is installed"
        return self.is_installed

    @property
    def version(self) -> str:
        "Version of the installed browser"
        return self._version

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass


class ChromeBrowser(BaseBrowser):
    def _get_version(self) -> str:
        return super()._get_version()

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass

class FirefoxBrowser(BaseBrowser):
    def _get_version(self) -> str:
        return super()._get_version()

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass


class AbstractWebdriver(ABC):
    @abstractmethod
    async def install(self, session: aiohttp.ClientSession) -> None:
        "Install the webdriver"

class BaseWebdriver(AbstractWebdriver):
    async def install(self, session: aiohttp.ClientSession) -> None:
        "Install the webdriver"
        return super().install(session)

class ChromeWebdriver(BaseWebdriver):
    async def install(self, session: aiohttp.ClientSession, install_path: pathlib.Path, version: str) -> None:
        "Install the webdriver"
        async with session.get("https://chromedriver.chromium.org/downloads") as response:
            soup = BeautifulSoup(response.text(), "lxml")

            page = soup.find("div", class_="tyJCtd mGzaTb Depvyb baZpAe")

            versions = []
            for para in page.children:
                para: Tag

                if para.find("a") is not None:
                    url = para.find("a").get("href")

                elif para.text.startswith("Supports Chrome version"):
                    start = int(para.text[-2])
                    end = int(para.text[-2]+1)
                    versions.append(
                        (url, range(start, end))
                        )

                elif para.text.startswith("Supports Chrome"):
                    end = int(para.text[-2])
                    start = int(para.text[-5:-3])
                    versions.append(
                        (url, range(start, end+1))
                        )

            for url, version in versions:
                if version == version:
                    async with session.get(url) as response:
                        soup = BeautifulSoup(response.text())
                        if os.name == "nt":
                            save_url = soup.find("a", text="chromedriver_win32.zip")

                        elif os.name == "posix":
                            save_url = soup.find("a", text="chromedriver_linux64.zip")

                    async with session.get(save_url) as response:
                        install_path.write_bytes(response.content)




class FirefoxWebdriver(BaseWebdriver):
    async def install(self, session: aiohttp.ClientSession, install_path: pathlib.Path) -> None:
        "Install the webdriver"
        async with session.get("https://github.com/mozilla/geckodriver/releases/latest") as response:
            if os.name == "unix":
                pass

            elif os.name == "nt":
                bit_arch = platform.architecture()[0]
                soup = BeautifulSoup(response.text(), "lxml")
                links = soup.find_all("li", class_="Box-row d-flex flex-column flex-md-row")
                for link in links:
                    if pathlib.Path(link.find("a").text).stem.endswith(f"win{bit_arch[:2]}"):
                        async with session.get("https://github.com" + link.find("a").get("href")) as response:
                            install_path.write_bytes(response.content)

class Webdrivers(Enum, BaseWebdriver):
    ChromeWebdriver = ChromeWebdriver()

class Browsers(Enum, BaseBrowser):
    ChromeBrowser = ChromeBrowser ()

