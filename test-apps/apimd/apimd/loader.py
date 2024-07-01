# -*- coding: utf-8 -*-

"""Compiler functions."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020-2021"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from typing import Optional
from collections.abc import Sequence, Iterator
from sys import path as sys_path
from os import mkdir, walk
from os.path import isdir, isfile, abspath, join, sep, dirname
from importlib.abc import Loader
from importlib.machinery import EXTENSION_SUFFIXES
from importlib.util import find_spec, spec_from_file_location, module_from_spec
from .logger import logger
from .parser import parent, Parser

PEP561_SUFFIX = '-stubs'


def _read(path: str) -> str:
    """Read the script from file."""
    with open(path, 'r') as f:
        return f.read()


def _write(path: str, doc: str) -> None:
    """Write text to the file."""
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(doc)


def _site_path(name: str) -> str:
    """Get the path in site-packages if exist."""
    s = find_spec(name)
    if s is None or s.submodule_search_locations is None:
        return ""
    return dirname(s.submodule_search_locations[0])


def walk_packages(name: str, path: str) -> Iterator[tuple[str, str]]:
    """Walk packages without import them."""
    path = abspath(path) + sep
    valid = (path + name, path + name + PEP561_SUFFIX)
    for root, _, fs in walk(path):
        for f in fs:
            if not f.endswith(('.py', '.pyi')):
                continue
            f_path = parent(join(root, f))
            if not f_path.startswith(valid):
                continue
            name = (f_path
                    .removeprefix(path)
                    .replace(PEP561_SUFFIX, "")
                    .replace(sep, '.')
                    .removesuffix('.__init__'))
            yield name, f_path


def _load_module(name: str, path: str, p: Parser) -> bool:
    """Load module directly."""
    # Load root first to avoid import error
    try:
        __import__(parent(name))
    except ImportError:
        return False
    s = spec_from_file_location(name, path)
    if s is not None and isinstance(s.loader, Loader):
        m = module_from_spec(s)
        s.loader.exec_module(m)
        p.load_docstring(name, m)
        return True
    return False


def loader(root: str, pwd: str, link: bool, level: int, toc: bool) -> str:
    """Package searching algorithm."""
    p = Parser.new(link, level, toc)
    for name, path in walk_packages(root, pwd):
        # Load its source or stub
        pure_py = False
        for ext in [".py", ".pyi"]:
            path_ext = path + ext
            if not isfile(path_ext):
                continue
            logger.debug(f"{name} <= {path_ext}")
            p.parse(name, _read(path_ext))
            if ext == ".py":
                pure_py = True
        if pure_py:
            continue
        logger.debug(f"loading extension module for fully documented:")
        # Try to load module here
        for ext in EXTENSION_SUFFIXES:
            path_ext = path + ext
            if not isfile(path_ext):
                continue
            logger.debug(f"{name} <= {path_ext}")
            if _load_module(name, path_ext, p):
                break
        else:
            logger.warning(f"no module for {name} in this platform")
    return p.compile()


def gen_api(
    root_names: dict[str, str],
    pwd: Optional[str] = None,
    *,
    prefix: str = 'docs',
    link: bool = True,
    level: int = 1,
    toc: bool = False,
    dry: bool = False
) -> Sequence[str]:
    """Generate API. All rules are listed in the readme.

    The path `pwd` is the current path that provided to `pkgutil`,
    which allows the "site-packages" directory to be used.
    """
    if pwd is not None:
        sys_path.append(pwd)
    if not isdir(prefix):
        logger.info(f"Create directory: {prefix}")
        mkdir(prefix)
    docs = []
    for title, name in root_names.items():
        logger.info(f"Load root: {name} ({title})")
        doc = loader(name, _site_path(name), link, level, toc)
        if not doc.strip():
            logger.warning(f"'{name}' can not be found")
            continue
        doc = '#' * level + f" {title} API\n\n" + doc
        path = join(prefix, f"{name.replace('_', '-')}-api.md")
        logger.info(f"Write file: {path}")
        if dry:
            logger.info('=' * 12)
            logger.info(doc)
        else:
            _write(path, doc)
        docs.append(doc)
    return docs
