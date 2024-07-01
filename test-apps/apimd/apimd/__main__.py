# -*- coding: utf-8 -*-

"""The command line launcher of apimd."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020-2021"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from argparse import ArgumentParser


def main() -> None:
    """Main function."""
    from apimd import __version__
    ver = f"apimd {__version__}"
    parser = ArgumentParser(
        prog=ver,
        description="Compile Python public API into Generic Markdown.",
        epilog=f"{__copyright__} {__license__} {__author__} {__email__}"
    )
    parser.add_argument('-v', '--version', action='version', version=ver)
    parser.add_argument(
        'module',
        default=None,
        nargs='+',
        type=str,
        help="the module name in the current path, use the syntax "
             "`Module-Name=module_name` to specify a name for it"
    )
    for cmd, f, h in [
        (('-c', '--current'), ".", "additional current directory"),
        (('-d', '--dir'), "docs", "output to a specific directory"),
    ]:
        parser.add_argument(*cmd, metavar="DIR", default=f, nargs='?',
                            type=str, help=h)
    parser.add_argument('--level', metavar="LEVEL", default=1, nargs='?',
                        type=int, help="the starting level of the sections")
    for cmd, h in [
        ('--toc', "generate table of contents"),
        ('--no-link', "don't use link anchor"),
        ('--dry', "show the result instead write the file"),
    ]:
        parser.add_argument(cmd, action='store_true', help=h)
    arg = parser.parse_args()
    root_names = {}
    for m in arg.module:  # type: str
        n = m.split('=', maxsplit=1)
        if len(n) == 1:
            n.append(n[0])
        if n[1] == "":
            n[1] = n[0]
        root_names[n[0]] = n[1]
    from apimd.loader import gen_api
    gen_api(root_names, arg.current, prefix=arg.dir, link=not arg.no_link,
            level=arg.level, toc=arg.toc, dry=arg.dry)


if __name__ == '__main__':
    main()
