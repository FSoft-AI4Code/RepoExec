[![Build status](https://img.shields.io/travis/KmolYuan/apimd.svg?logo=travis)](https://travis-ci.org/KmolYuan/apimd)
[![PyPI](https://img.shields.io/pypi/v/apimd.svg)](https://pypi.org/project/apimd/)

# apimd

A Python API compiler for universal Markdown syntax.

Required Python 3.9 and above. (for `ast.unparse` function)

This parser using `ast` standard library to extract the type annotations (without inference) and docstrings, similar to MyPy.
The target modules must be from at least Python 3.0, which is the lowest version with `ast` support.

A self-compiled example is presented at <https://github.com/KmolYuan/apimd/blob/master/docs/apimd-api.md>.

## Install

Install by pip:

```bash
pip install apimd
```

From Git repository:

```bash
pip install .
```

## Command Line Interface

Following syntax are allowed:

```bash
apimd module_name
apimd Module-Name=module_name
apimd "Module Name=module_name"
```

The first is the readable name of the package,
and the second is the name used in import syntax.

The output path can be chosen by `-d` or `--dir` option, default is `docs`.
Multiple modules are supported either.

```bash
apimd module1 module2 -d out_path
```

If you just want to show output, use dry run mode.

```bash
apimd module --dry
```

## Rules

Basically, this compiler can extract docstrings and annotations from those "public" names:
(PEP [484], [526])

+ Modules
+ Functions & Generators (support async version)
+ Classes and its methods

According to PEP 8, "**public**" means a name can't start with underscore symbol `_`, except magic methods.
If the public name (other than the magic name) has no docstring, the compiler will issue a warning.
([Naming Conventions])

The names must be defined within the scope of module and class,
and supports the use of `if` and `try` statements.

### Constants

Constants (upper snake case) are no docstring their owned but still listed in module section.
Please mention them in the module docstring.

### Constant Type Inference

Constant type inference applies to built-in types and containers with built-in types,
such as `None`, `int`, `bool`, `str`, `tuple`, `dict[int, str]`, etc.
You can also annotate them manually.

This function also works in class attributes, but doesn't support unpacking.

### Import Inference

A module should list the objects `__all__` to prevent other public style names.
In this parser, wildcard import syntax (`from ... import *`) will be ignored,
which will cause the name from the statement will lose its parent module.
If there has any import statements in the package root `__init__.py`,
the API can be substituted into a short name, for example, change `a.b.c` to `a.c`.
([Global Variable Names])

### Generic Self

To avoid generic self-reference that is not easy to understand,
the compiler introduce `Self` type concept from [Rust language],
which means the first argument in class should be treated as it and its subclasses.

```python
def method(self, a: int) -> None:
    ...
```

| self | a | return |
|:----:|:---:|:----:|
| `Self` | `int` | `None` |

If a method returns its self, in Python, it can be mark as:

```python
class A:
    _Self = typing.TypeVar('_Self', bound='A')
    def method(self: _Self) -> _Self:
        return self
    @classmethod
    def make_method(cls: typing.Type[_Self]) -> _Self:
        return cls()
```

| self | return |
|:----:|:------:|
| `Self` | `Self` |

| cls | return |
|:----:|:------:|
| `type[Self]` | `Self` |

The example shown at [self-compiled documentation](./docs/apimd-api.md#apimd-parser-parser-new).

### Improvement from PEPs

In addition to the basic rules, your documentation will be improved for accepted PEPs,
even it is only implemented in the future version.
(your code still will not be modified)

| No. | Description |
|:---:|:------------|
| [585] | Type Hinting Generics In Standard Collections |
| [604] | Allow writing union types as X &#124; Y |

### Section Links

Since the converted title id will remove the period symbol,
apimd will insert another HTML anchor id to help you refer to other public names in docstring.
The anchor id is generated from the lowercase full name,
and replace the periods `.` by hyphens `-`.
For example, `aaa.AAA.bbb_Ccc` will become `aaa-aaa-bbb_ccc`.

Use `--no-link` to prevent this function.

### Generating Table of Contents

Add `--toc` option to generate the table of contents at the top of the document.
This option will force activate section link option.

## Stubs

If a module has a stub file (`.pyi`), the stub file will be loaded for annotations once again.
Docstrings should still be written in the module first.
For extensions (`.so`, `.pyd` or `.dylib` with Python version suffix), this tool will try to load the docstrings from module
if `.py` file is not found.

[Naming Conventions]: https://www.python.org/dev/peps/pep-0008/#naming-conventions
[Global Variable Names]: https://www.python.org/dev/peps/pep-0008/#global-variable-names
[484]: https://www.python.org/dev/peps/pep-0484/
[526]: https://www.python.org/dev/peps/pep-0526/
[585]: https://www.python.org/dev/peps/pep-0585/
[604]: https://www.python.org/dev/peps/pep-0585/
[Rust language]: https://www.rust-lang.org/
