# -*- coding: utf-8 -*-

"""Implementation of PEP585 deprecated name alias."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2020-2021"
__license__ = "MIT"
__email__ = "pyslvs@gmail.com"

PEP585 = {
    'typing.Tuple': 'tuple',
    'typing.List': 'list',
    'typing.Dict': 'dict',
    'typing.Set': 'set',
    'typing.FrozenSet': 'frozenset',
    'typing.Type': 'type',
    'typing.Deque': 'collections.deque',
    'typing.DefaultDict': 'collections.defaultdict',
    'typing.OrderedDict': 'collections.OrderedDict',
    'typing.Counter': 'collections.Counter',
    'typing.ChainMap': 'collections.ChainMap',
    'typing.Awaitable': 'collections.abc.Awaitable',
    'typing.Coroutine': 'collections.abc.Coroutine',
    'typing.AsyncIterable': 'collections.abc.AsyncIterable',
    'typing.AsyncIterator': 'collections.abc.AsyncIterator',
    'typing.Iterable': 'collections.abc.Iterable',
    'typing.Iterator': 'collections.abc.Iterator',
    'typing.Generator': 'collections.abc.Generator',
    'typing.Reversible': 'collections.abc.Reversible',
    'typing.Container': 'collections.abc.Container',
    'typing.Collection': 'collections.abc.Collection',
    'typing.AbstractSet': 'collections.abc.Set',
    'typing.MutableSet': 'collections.abc.MutableSet',
    'typing.Mapping': 'collections.abc.Mapping',
    'typing.MutableMapping': 'collections.abc.MutableMapping',
    'typing.Sequence': 'collections.abc.Sequence',
    'typing.MutableSequence': 'collections.abc.MutableSequence',
    'typing.ByteString': 'collections.abc.ByteString',
    'typing.MappingView': 'collections.abc.MappingView',
    'typing.KeysView': 'collections.abc.KeysView',
    'typing.ItemsView': 'collections.abc.ItemsView',
    'typing.ValuesView': 'collections.abc.ValuesView',
    'typing.ContextManager': 'contextlib.AbstractContextManager',
    'typing.AsyncContextManager': 'contextlib.AsyncContextManager',
    'typing.Pattern': 're.Pattern',
    'typing.re.Pattern': 're.Pattern',
    'typing.Match': 're.Match',
    'typing.re.Match': 're.Match',
}
