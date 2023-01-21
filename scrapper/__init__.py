import csv
import json
import pathlib
import typing


class SingletonMeta(type):
    def __init__(self, _, __, ___) -> None:
        self.__instance = None

    def __call__(self, *args: typing.Any, **kwds: typing.Any) -> typing.Any:
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwds)

        return self.__instance


class System(
    metaclass = SingletonMeta
    ):
    def __init__(self) -> None:
        self.__package_path = pathlib.Path(__file__).parent
        self.__path_to_webdrivers: pathlib.Path = self.__package_path / "webdrivers"

        settings: dict = self.__get_settings()

        self.__phrase_table: dict = self.__create_frase_table(settings)
        self.__logging_template: dict = settings["logging configuration"]
        self.__debug: bool = False
        self.__path_to_scrappers: pathlib.Path = settings["path to scrappers"]

    @property
    def phrase_table(self) -> dict:
        return self.__phrase_table

    @property
    def logging_template(self) -> dict:
        return self.__logging_template

    @property
    def debug(self) -> bool:
        return self.__debug

    @property
    def path_to_scrappers(self) -> pathlib.Path:
        return self.__path_to_scrappers


    @property
    def path_to_webdrivers(self) -> pathlib.Path:
        return self.__path_to_webdrivers

    @property
    def path_to_firefox(self) -> pathlib.Path:
        return self.__path_to_webdrivers / "geckodriver.exe"

    @property
    def path_to_chrome(self) -> pathlib.Path:
        return self.__path_to_webdrivers / "chromedriver.exe"


    def set_debug(self) -> None:
        "Set debug to True"
        self.__debug = True


    def __get_settings(self) -> dict:
        settings_path = self.__package_path / "settings.json"
        return json.loads(settings_path.read_text())

    def __create_frase_table(self, settings: dict) -> dict:
        frase_table_path = self.__package_path / "frase_table.csv"
        frase_table = {}
        language: str = settings["language"]

        csv_reader = csv.DictReader(
            f = frase_table_path.read_text("utf-8").splitlines(),
            fieldnames = ("Constant", "RU", "EN"),
            escapechar = '"'
            )
        for raw in csv_reader:
            frase_table[raw["Constant"]] = raw[language]

        return frase_table
