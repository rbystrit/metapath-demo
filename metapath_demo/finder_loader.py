from genericpath import isfile
import fsspec
from importlib.abc import SourceLoader, MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_loader
from typing import Union, Dict, List
from pathlib import PurePosixPath
from os import fspath


_Path = Union[str, bytes]


class FSSpecFinder(MetaPathFinder):
    def __init__(self, fs: fsspec.AbstractFileSystem, root: _Path = None) -> None:
        self._fs = fs
        self._root = root
        super().__init__()

    @property
    def filesystem(self):
        return self._fs

    @property
    def root(self):
        return self._root

    def find_spec(self, fullname: str, path: Union[None, List[_Path]], target=None) -> ModuleSpec:
        if not path:
            loader = FSSpecLoader(self._fs, self._root)
            return spec_from_loader(fullname, loader)
        else:
            if "." in fullname:
                _, _, name = fullname.rpartition(".")
            else:
                name = fullname

            for p in path:
                loader = FSSpecLoader(self._fs, self._root)
                try:
                    spec = spec_from_loader(name, loader)
                    if spec is not None:
                        spec.name = fullname
                        spec.loader = FSSpecLoader(self._fs, self._root)
                        return spec
                except Exception:
                    pass

    def find_module(self, fullname: str, path: str) -> Loader:
        spec = self.find_spec(fullname, path)
        if spec is not None:
            return spec.loader
        return None


class FSSpecLoader(SourceLoader):
    def __init__(self, fs: fsspec.AbstractFileSystem, root: _Path = None, filename: _Path = None) -> None:
        self._fs = fs
        self._root = root
        self._filename = filename

    def get_filename(self, fullname: str) -> str:

        if self._filename is not None:
            return self._filename

        partial_file = fullname.replace(".", "/")
        module_path = fspath(PurePosixPath(self._root).joinpath(partial_file)) + ".py"
        package_path = fspath(PurePosixPath(self._root).joinpath(
            partial_file, "__init__")) + ".py"

        if self._fs.isfile(module_path):
            return module_path

        if self._fs.isfile(package_path):
            return package_path

        raise ImportError

    def get_data(self, path: _Path) -> bytes:
        with self._fs.open(path, "rb") as f:
            return f.read()
