

import pathlib

from ..scrapper import System


def test_root_path(tmp_path: pathlib.Path):
        package_path = tmp_path / "package"
        package_path.mkdir(exist_ok=True, parents=True)
        scrapper_path = tmp_path / "sc"
        scrapper_path.mkdir(exist_ok=True, parents=True)
        assert System().package_path == package_path
