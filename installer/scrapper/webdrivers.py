from __future__ import annotations

import os
from abc import ABC, abstractmethod, abstractproperty

import aiohttp
from bs4 import BeautifulSoup, Tag

from . import SingletonMeta


class AbstractBrowser(ABC, metaclass=SingletonMeta):
    @abstractproperty
    def is_installed(self) -> bool:
        "Return if the browser is installed"

    @abstractproperty
    def version(self) -> str:
        "Version of installed browser"

class BaseBrowser(AbstractBrowser, metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._is_installed = self._get_is_installed()
        self._version = self._get_version()

    @property
    def version(self) -> str:
        return self._version

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass


class ChromeBrowser(BaseBrowser, metaclass=SingletonMeta):
    def _get_version(self) -> str:
        return super()._get_version()

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass

class FirefoxBrowser(BaseBrowser, metaclass=SingletonMeta):
    def _get_version(self) -> str:
        return super()._get_version()

    def _get_version(self) -> str:
        pass

    def _get_is_installed(self) -> bool:
        pass


class AbstractWebdriver(ABC, metaclass=SingletonMeta):
    @abstractmethod
    async def install(self, session: aiohttp.ClientSession) -> None:
        "Install the webdriver"

class BaseWebdriver(AbstractWebdriver, metaclass=SingletonMeta):
    async def install(self, session: aiohttp.ClientSession) -> None:
        return super().install(session)

class ChromeWebdriver(BaseWebdriver, metaclass=SingletonMeta):
    async def install(self, session: aiohttp.ClientSession) -> None:
        async with session.get("https://chromedriver.chromium.org/downloads") as response:
            soup = BeautifulSoup(response.text(), "lxml")

            page = soup.find("div", class_="tyJCtd mGzaTb Depvyb baZpAe")

            versions = []
            for para in page.children:
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
                if version == ChromeBrowser().version:
                    async with session.get(url) as response:
                        soup = BeautifulSoup(response.text())
                        if os.name == "nt":
                            soup.find("a")

                        elif os.name == "":
                            pass




class FirefoxWebdriver(BaseWebdriver, metaclass=SingletonMeta):
    async def install(self, session: aiohttp.ClientSession) -> None:
        return super().install()


WEBDRIVERS = (ChromeWebdriver())
BROWSERS = (ChromeBrowser())
