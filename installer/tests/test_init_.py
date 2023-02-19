import pathlib

from .. import scrapper


def test_package_path():
        package_path = pathlib.Path(scrapper.__file__) / "package"
        assert scrapper.System().package_path == package_path
