import pathlib

from ..scrapper.prepare_package import Package


def test_path_to_scrappers(tmp_path: pathlib.Path):
    root_path = tmp_path / "package"
    root_path.mkdir(exist_ok=True, parents=True)
    scrapper_path = tmp_path / "sc"
    scrapper_path.mkdir(exist_ok=True, parents=True)
    assert Package(root_path, scrapper_path).path_to_scrappers == scrapper_path
