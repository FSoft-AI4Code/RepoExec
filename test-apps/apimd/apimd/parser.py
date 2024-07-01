# -*- coding: utf-8 -*-

"""Data structures."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020-2021"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

from typing import cast, TypeVar, Union, Optional
from types import ModuleType
from collections.abc import Sequence, Iterable, Iterator
from itertools import chain
from dataclasses import dataclass, field
from inspect import getdoc
from ast import (
    parse, unparse, get_docstring, AST, FunctionDef, AsyncFunctionDef, ClassDef,
    Assign, AnnAssign, Delete, Import, ImportFrom, Name, Expr, Subscript, BinOp,
    BitOr, Call, If, Try, Tuple, List, Set, Dict, Constant, Load, Attribute,
    arg, expr, stmt, arguments, NodeTransformer,
)
from .logger import logger
from .pep585 import PEP585

_I = Union[Import, ImportFrom]
_G = Union[Assign, AnnAssign]
_API = Union[FunctionDef, AsyncFunctionDef, ClassDef]
ANY = 'Any'


def _m(*names: str) -> str:
    """Get module names"""
    return '.'.join(s for s in names if s)


def _attr(obj: object, attr: str) -> object:
    """Nest `getattr` function."""
    n = obj
    for p in attr.split('.'):
        n = getattr(n, p, None)
        if n is None:
            return None
    return n


def _defaults(args: Sequence[Optional[expr]]) -> Iterator[str]:
    """Literals of the table."""
    yield from (code(unparse(a)) if a is not None else " " for a in args)


def parent(name: str, *, level: int = 1) -> str:
    """Get parent name with level."""
    return name.rsplit('.', maxsplit=level)[0]


def is_magic(name: str) -> bool:
    """Check magic name."""
    name = name.rsplit('.', maxsplit=1)[-1]
    return name[:2] == name[-2:] == '__'


def is_public_family(name: str) -> bool:
    """Check the name is come from public modules or not."""
    for n in name.split('.'):
        # Magic name
        if is_magic(n):
            continue
        # Local or private name
        if n.startswith('_'):
            return False
    return True


def walk_body(body: Sequence[stmt]) -> Iterator[stmt]:
    """Traverse around body and its simple definition scope."""
    for node in body:
        if isinstance(node, If):
            yield from walk_body(node.body)
            yield from walk_body(node.orelse)
        elif isinstance(node, Try):
            yield from walk_body(node.body)
            for h in node.handlers:
                yield from walk_body(h.body)
            yield from walk_body(node.orelse)
            yield from walk_body(node.finalbody)
        else:
            yield node


def code(doc: str) -> str:
    """Escape Markdown charters from inline code."""
    doc = doc.replace('|', '&#124;')
    if '&' in doc:
        return f"<code>{doc}</code>"
    elif doc:
        return f"`{doc}`"
    else:
        return " "


def esc_underscore(doc: str) -> str:
    """Escape underscore in names."""
    if doc.count('_') > 1:
        return doc.replace('_', r"\_")
    else:
        return doc


def doctest(doc: str) -> str:
    """Wrap doctest as markdown Python code."""
    keep = False
    docs = []
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        signed = line.startswith(">>> ")
        if signed:
            if not keep:
                docs.append("```python")
                keep = True
        elif keep:
            docs.append("```")
            keep = False
        docs.append(line)
        if signed and i == len(lines) - 1:
            docs.append("```")
            keep = False
    return '\n'.join(docs)


def _table_cell(items: Iterable[str]) -> str:
    """Make a row of table cell."""
    return '|' + '|'.join(f" {t} " for t in items) + '|'


def _table_split(args: Iterable[str]) -> str:
    """The split line of the table."""
    return '|' + '|'.join(":" + '-' * (len(a) if len(a) > 3 else 3) + ":"
                          for a in args) + '|'


def table(*titles: str, items: Iterable[Union[str, Iterable[str]]]) -> str:
    """Create multi-column table with the titles.

    Usage:
    >>> table('a', 'b', [['c', 'd'], ['e', 'f']])
    | a | b |
    |:---:|:---:|
    | c | d |
    | e | f |
    """
    return '\n'.join([_table_cell(titles), _table_split(titles),
                      '\n'.join(_table_cell([n] if isinstance(n, str) else n)
                                for n in items)]) + '\n\n'


def _type_name(obj: object) -> str:
    """Get type name."""
    return type(obj).__qualname__


def _e_type(*elements: Sequence[Optional[expr]]) -> str:
    """Get element type if type is constants."""
    if not elements:
        return ""
    ts = []
    for element in elements:
        if not element:
            return ""
        t = ""
        for e in element:
            if not isinstance(e, Constant):
                return ""
            nw_t = _type_name(e.value)
            if t and t != nw_t:
                t = "Any"
                break
            t = nw_t
        ts.append(t)
    return '[' + ", ".join(ts) + ']'


def const_type(node: expr) -> str:
    """Constant type inference."""
    if isinstance(node, Constant):
        return _type_name(node.value)
    elif isinstance(node, (Tuple, List, Set)):
        return _type_name(node).lower() + _e_type(node.elts)
    elif isinstance(node, Dict):
        return 'dict' + _e_type(node.keys, node.values)
    elif isinstance(node, Call) and isinstance(node.func, (Name, Attribute)):
        func = unparse(node.func)
        if func in chain({'bool', 'int', 'float', 'complex', 'str'},
                         PEP585.keys(), PEP585.values()):
            return func
    return ANY


class Resolver(NodeTransformer):
    """Annotation resolver."""

    def __init__(self, root: str, alias: dict[str, str], self_ty: str = ""):
        """Set root module, alias and generic self name."""
        super(Resolver, self).__init__()
        self.root = root
        self.alias = alias
        self.self_ty = self_ty

    def visit_Constant(self, node: Constant) -> AST:
        """Check string is a name."""
        if not isinstance(node.value, str):
            return node
        try:
            e = cast(Expr, parse(node.value).body[0])
        except SyntaxError:
            return node
        else:
            return self.visit(e.value)

    def visit_Name(self, node: Name) -> AST:
        """Replace global names with its expression recursively."""
        if node.id == self.self_ty:
            return Name("Self", Load())
        name = _m(self.root, node.id)
        if name in self.alias and name not in self.alias[name]:
            e = cast(Expr, parse(self.alias[name]).body[0])
            # Support `TypeVar`
            if isinstance(e.value, Call) and isinstance(e.value.func, Name):
                func_name = e.value.func.id
                idf = self.alias.get(_m(self.root, func_name), func_name)
                if idf == 'typing.TypeVar':
                    return node
            return self.visit(e.value)
        else:
            return node

    def visit_Subscript(self, node: Subscript) -> AST:
        """Implementation of PEP585 and PEP604."""
        if not isinstance(node.value, Name):
            return node
        name = node.value.id
        idf = self.alias.get(_m(self.root, name), name)
        if idf == 'typing.Union':
            if not isinstance(node.slice, Tuple):
                return node.slice
            b = node.slice.elts[0]
            for e in node.slice.elts[1:]:
                b = BinOp(b, BitOr(), e)
            return b
        elif idf == 'typing.Optional':
            return BinOp(node.slice, BitOr(), Constant(None))
        elif idf in PEP585:
            logger.warning(f"{node.lineno}:{node.col_offset}: "
                           f"find deprecated name {idf}, "
                           f"recommended to use {PEP585[idf]}")
            return Subscript(Name(PEP585[idf], Load), node.slice, node.ctx)
        else:
            return node

    def visit_Attribute(self, node: Attribute) -> AST:
        """Remove `typing.*` prefix of annotation."""
        if not isinstance(node.value, Name):
            return node
        if node.value.id == 'typing':
            return Name(node.attr, Load())
        else:
            return node


@dataclass
class Parser:
    """AST parser.

    Usage:
    >>> p = Parser()
    >>> with open("pkg_path", 'r') as f:
    >>>     p.parse('pkg_name', f.read())
    >>> s = p.compile()

    Or create with parameters:
    >>> p = Parser.new(link=True, level=1)
    """
    link: bool = True
    b_level: int = 1
    toc: bool = False
    level: dict[str, int] = field(default_factory=dict)
    doc: dict[str, str] = field(default_factory=dict)
    docstring: dict[str, str] = field(default_factory=dict)
    imp: dict[str, set[str]] = field(default_factory=dict)
    root: dict[str, str] = field(default_factory=dict)
    alias: dict[str, str] = field(default_factory=dict)
    const: dict[str, str] = field(default_factory=dict)
    _Self = TypeVar('_Self', bound='Parser')

    @classmethod
    def new(cls: type[_Self], link: bool, level: int, toc: bool) -> _Self:
        """Create a parser by options."""
        return cls(link, level, toc)

    def __post_init__(self):
        if self.toc:
            self.link = True

    def parse(self, root: str, script: str) -> None:
        """Main parser of the entire module."""
        self.doc[root] = '#' * self.b_level + "# Module `{}`"
        if self.link:
            self.doc[root] += "\n<a id=\"{}\"></a>"
        self.doc[root] += '\n\n'
        self.level[root] = root.count('.')
        self.imp[root] = set()
        self.root[root] = root
        root_node = parse(script, type_comments=True)
        for node in walk_body(root_node.body):
            # "Execute" assignments
            if isinstance(node, (Import, ImportFrom)):
                self.imports(root, node)
            elif isinstance(node, (Assign, AnnAssign)):
                self.globals(root, node)
        doc = get_docstring(root_node)
        if doc is not None:
            self.docstring[root] = doctest(doc)
        for node in walk_body(root_node.body):
            if isinstance(node, (FunctionDef, AsyncFunctionDef, ClassDef)):
                self.api(root, node)

    def imports(self, root: str, node: _I) -> None:
        """Save import names."""
        if isinstance(node, Import):
            for a in node.names:
                name = a.name if a.asname is None else a.asname
                self.alias[_m(root, name)] = a.name
        elif node.module is not None:
            if node.level:
                m = parent(root, level=node.level - 1)
            else:
                m = ''
            for a in node.names:
                name = a.name if a.asname is None else a.asname
                self.alias[_m(root, name)] = _m(m, node.module, a.name)

    def globals(self, root: str, node: _G) -> None:
        """Set up globals:

        + Type alias
        + Constants
        + `__all__` filter
        """
        if (
            isinstance(node, AnnAssign)
            and isinstance(node.target, Name)
            and node.value is not None
        ):
            left = node.target
            expression = unparse(node.value)
            ann = self.resolve(root, node.annotation)
        elif (
            isinstance(node, Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], Name)
        ):
            left = node.targets[0]
            expression = unparse(node.value)
            if node.type_comment is None:
                ann = const_type(node.value)
            else:
                ann = node.type_comment
        else:
            return
        name = _m(root, left.id)
        self.alias[name] = expression
        if left.id.isupper():
            self.root[name] = root
            if self.const.get(name, ANY) == ANY:
                self.const[name] = ann
        if left.id != '__all__' or not isinstance(node.value, (Tuple, List)):
            return
        for e in node.value.elts:
            if isinstance(e, Constant) and isinstance(e.value, str):
                self.imp[root].add(_m(root, e.value))

    def api(self, root: str, node: _API, *, prefix: str = '') -> None:
        """Create API doc for only functions and classes.
        Where `name` is the full name.
        """
        level = '#' * (self.b_level + (2 if not prefix else 3))
        name = _m(root, prefix, node.name)
        self.level[name] = self.level[root]
        self.root[name] = root
        shirt_name = esc_underscore(_m(prefix, node.name))
        if isinstance(node, FunctionDef):
            self.doc[name] = f"{level} {shirt_name}()\n\n"
        elif isinstance(node, AsyncFunctionDef):
            self.doc[name] = f"{level} async {shirt_name}()\n\n"
        else:
            self.doc[name] = f"{level} class {shirt_name}\n\n"
        self.doc[name] += "*Full name:* `{}`"
        if self.link:
            self.doc[name] += "\n<a id=\"{}\"></a>"
        self.doc[name] += '\n\n'
        decs = ['@' + self.resolve(root, d) for d in node.decorator_list]
        if decs:
            self.doc[name] += table("Decorators", items=map(code, decs))
        if isinstance(node, (FunctionDef, AsyncFunctionDef)):
            self.func_api(root, name, node.args, node.returns,
                          has_self=bool(prefix) and '@staticmethod' not in decs,
                          cls_method='@classmethod' in decs)
        else:
            self.class_api(root, name, node.bases, node.body)
        doc = get_docstring(node)
        if doc is not None:
            self.docstring[name] = doctest(doc)
        if not isinstance(node, ClassDef):
            return
        for e in walk_body(node.body):
            if isinstance(e, (FunctionDef, AsyncFunctionDef, ClassDef)):
                self.api(root, e, prefix=node.name)

    def func_api(self, root: str, name: str, node: arguments,
                 returns: Optional[expr], *,
                 has_self: bool, cls_method: bool) -> None:
        """Create function API."""
        args = []
        default: list[Optional[expr]] = []
        if node.posonlyargs:
            args.extend(node.posonlyargs)
            args.append(arg('/', None))
            default.extend([None] * len(node.posonlyargs))
        args.extend(node.args)
        default.extend([None] * (len(node.args) - len(node.defaults)))
        default.extend(node.defaults)
        if node.vararg is not None:
            args.append(arg('*' + node.vararg.arg, node.vararg.annotation))
        elif node.kwonlyargs:
            args.append(arg('*', None))
        default.append(None)
        args.extend(node.kwonlyargs)
        default.extend([None] * (len(node.kwonlyargs) - len(node.kw_defaults)))
        default.extend(node.kw_defaults)
        if node.kwarg is not None:
            args.append(arg('**' + node.kwarg.arg, node.kwarg.annotation))
            default.append(None)
        args.append(arg('return', returns))
        default.append(None)
        ann = map(code, self.func_ann(root, args, has_self=has_self,
                                      cls_method=cls_method))
        has_default = all(d is None for d in default)
        self.doc[name] += table(
            *(a.arg for a in args),
            items=[ann] if has_default else [ann, _defaults(default)])

    def class_api(self, root: str, name: str, bases: list[expr],
                  body: list[stmt]) -> None:
        """Create class API."""
        r_bases = [self.resolve(root, d) for d in bases]
        if r_bases:
            self.doc[name] += table("Bases", items=map(code, r_bases))
        is_enum = any(map(lambda s: s.startswith('enum.'), r_bases))
        mem = {}
        enums = []
        for node in walk_body(body):
            if isinstance(node, AnnAssign) and isinstance(node.target, Name):
                attr = node.target.id
                if is_enum:
                    enums.append(attr)
                elif is_public_family(attr):
                    mem[attr] = self.resolve(root, node.annotation)
            elif (
                isinstance(node, Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], Name)
            ):
                attr = node.targets[0].id
                if is_enum:
                    enums.append(attr)
                elif is_public_family(attr):
                    if node.type_comment is None:
                        mem[attr] = const_type(node.value)
                    else:
                        mem[attr] = node.type_comment
            elif isinstance(node, Delete):
                for d in node.targets:
                    if not isinstance(d, Name):
                        continue
                    attr = d.id
                    mem.pop(attr, None)
                    if attr in enums:
                        enums.remove(attr)
        if enums:
            self.doc[name] += table("Enums", items=enums)
        elif mem:
            self.doc[name] += table('Members', 'Type', items=(
                (code(n), code(mem[n])) for n in sorted(mem)))

    def func_ann(self, root: str, args: Sequence[arg], *,
                 has_self: bool, cls_method: bool) -> Iterator[str]:
        """Function annotation table."""
        self_ty = ""
        for i, a in enumerate(args):
            if has_self and i == 0:
                if a.annotation is not None:
                    self_ty = self.resolve(root, a.annotation)
                    if cls_method:
                        self_ty = (self_ty.removeprefix('type[')
                                   .removesuffix(']'))
                yield 'type[Self]' if cls_method else 'Self'
            elif a.arg == '*':
                yield ""
            elif a.annotation is not None:
                yield self.resolve(root, a.annotation, self_ty)
            else:
                yield ANY

    def resolve(self, root: str, node: expr, self_ty: str = "") -> str:
        """Search and resolve global names in annotation."""
        r = Resolver(root, self.alias, self_ty)
        return unparse(r.generic_visit(r.visit(node)))

    def load_docstring(self, root: str, m: ModuleType) -> None:
        """Load docstring from the module."""
        for name in self.doc:
            if not name.startswith(root):
                continue
            attr = name.removeprefix(root + '.')
            doc = getdoc(_attr(m, attr))
            if doc is not None:
                self.docstring[name] = doctest(doc)

    def __is_immediate_family(self, n1: str, n2: str) -> bool:
        """Check the name is immediate family."""
        return n2.startswith(n1.removesuffix(n2.removeprefix(self.root[n2])))

    def __find_alias(self):
        """Alias substitution."""
        for n, a in self.alias.items():
            if a not in self.doc or not self.__is_immediate_family(n, a):
                continue
            for ch in list(self.doc):
                if not ch.startswith(a):
                    continue
                nw = n + ch.removeprefix(a)
                self.doc[nw] = self.doc.pop(ch)
                self.docstring[nw] = self.docstring.pop(ch, "")
                name = ch.removeprefix(self.root.pop(ch))
                self.root[nw] = nw.removesuffix(name)
                self.level.pop(ch)
                self.level[nw] = self.root[nw].count('.')
                if ch in self.const:
                    self.const[nw] = self.const.pop(ch)

    def is_public(self, s: str) -> bool:
        """Check the name is public style or listed in `__all__`."""
        if s in self.imp:
            for ch in chain(self.doc.keys(), self.const.keys()):
                if ch.startswith(s + '.') and is_public_family(ch):
                    break
            else:
                return False
        all_l = self.imp[self.root[s]]
        if all_l:
            return s == self.root[s] or bool({s, parent(s)} & all_l)
        else:
            return is_public_family(s)

    def __get_const(self, name: str) -> str:
        """Get constants table."""
        const = []
        for c in self.const:
            if self.root[c] == name and self.is_public(c):
                ch = c.removeprefix(name + '.')
                const.append((code(ch), code(self.const[c])))
        if const:
            return table('Constants', 'Type', items=const)
        else:
            return ""

    def __names_cmp(self, s: str) -> tuple[int, str, bool]:
        """Name comparison function."""
        return self.level[s], s.lower(), not s.islower()

    def compile(self) -> str:
        """Compile documentation."""
        self.__find_alias()
        toc = ['**Table of contents:**']
        docs = []
        for name in sorted(self.doc, key=self.__names_cmp):
            if not self.is_public(name):
                continue
            link = name.lower().replace('.', '-')
            doc = self.doc[name].format(name, link)
            if name in self.imp:
                doc += self.__get_const(name)
            if name in self.docstring:
                doc += self.docstring[name]
            elif is_magic(name):
                continue
            else:
                logger.warning(f"Missing documentation for {name}")
            level = name.removeprefix(self.root[name]).count('.')
            toc.append(" " * 4 * level + f"+ [{code(name)}](#{link})")
            docs.append(doc.rstrip())
        if self.toc:
            return '\n'.join(toc) + '\n\n' + "\n\n".join(docs) + '\n'
        return "\n\n".join(docs) + '\n'
