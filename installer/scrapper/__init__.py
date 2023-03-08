import csv
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
        language = input("Choose your language (RU/EN):")
        if language not in ("RU", "EN"):
            raise Exception(f"Unexpected language: {language}")

        self.__package_path = pathlib.Path(__file__).parent
        self.__phrase_table = self.__create_frase_table(language)

    @property
    def package_path(self) -> pathlib.Path:
        return self.__package_path

    @property
    def phrase_table(self) -> dict:
        return self.__phrase_table

    def __create_frase_table(self, language: str) -> dict:
        frase_table_path = self.__package_path / "frase_table.csv"
        frase_table = {}

        csv_reader = csv.DictReader(
            f = frase_table_path.read_text("utf-8").splitlines(),
            fieldnames = ("Constant", "RU", "EN"),
            escapechar = '"'
            )
        for raw in csv_reader:
            frase_table[raw["Constant"]] = raw[language]

        return frase_table
