from metapath_demo import __version__
from metapath_demo.finder_loader import FSSpecFinder, FSSpecLoader

import fsspec
import sys
import os.path


def test_version():
    assert __version__ == "0.1.0"


def test_import_package():
    fs = fsspec.filesystem("file")
    finder = FSSpecFinder(fs, os.path.join(os.path.dirname(__file__), "_test_data"))
    try:
        sys.meta_path.insert(0, finder)

        import _test_package  # noqa: F401
    finally:
        sys.meta_path.remove(finder)

    assert isinstance(_test_package.__loader__, FSSpecLoader)


def test_import_package_github():
    fs = fsspec.filesystem("github", org="rbystrit", repo="metapath_test_project")
    finder = FSSpecLoader(fs)
    try:
        sys.meta_path.insert(0, finder)

        import metapath_test_project  # noqa: F401
    finally:
        sys.meta_path.remove(finder)

    assert isinstance(metapath_test_project.__loader__, FSSpecLoader)
