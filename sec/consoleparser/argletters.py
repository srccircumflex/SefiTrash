# MIT License
#
# Copyright (c) 2022 Adrian F. Hoefflin [srccircumflex]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import annotations

from ast import literal_eval
from copy import deepcopy

try:
    from .. import consoleparser
except ImportError:
    import consoleparser

class _ArgLetter:
    def __init__(self):
        self.mod = 1
        self.mod_info_wrappers = {
            -3: lambda label: consoleparser._PRINTING.MOD_WRAPPER_INF_OPTIONAL % label,
            -2 : lambda label: consoleparser._PRINTING.MOD_WRAPPER_EOL_OPTIONAL % label,
            -1: lambda label: consoleparser._PRINTING.MOD_WRAPPER_OPTIONAL % label,
            1: lambda label: consoleparser._PRINTING.MOD_WRAPPER % label,
            2: lambda label: consoleparser._PRINTING.MOD_WRAPPER_EOL % label,
            3: lambda label: consoleparser._PRINTING.MOD_WRAPPER_INF % label
        }
        self._label = None

    def __config__(self) -> str:
        opt = (" & -1" if self.mod < 0 else "")
        mod = (" & %d" % self.mod.__abs__() if self.mod.__abs__() in (2, 3) else "")
        lab = (None if self._label is None else f"{self._label!r}")
        return f"%s.%s().label(%s)%s%s" % (self.__module__.split('.')[1], self.__class__.__name__, lab, opt, mod)

    def label(self, __label: str | None) -> _ArgLetter:
        __c = deepcopy(self)
        __c._label = __label
        return __c

    def _vmod(self, __cls: _ArgLetter) -> None | AttributeError:
        if __cls.mod not in self.mod_info_wrappers:
            raise consoleparser.Exceptions.ConfigError(f"{__cls.__repr__.__qualname__.split('.')[0]} <-> {__cls.mod}")
        return

    def __eq__(self, other):
        return other == self.mod

    def __and__(self, other):
        __c = deepcopy(self)
        __c.mod = self.mod * int(other)
        self._vmod(__c)
        return __c

    def __or__(self, other):
        self.__repr__()
        other.__repr__()
        __c = deepcopy(other)
        __c._label = "(%s%s%s)" % (self._label, consoleparser._PRINTING.OR, other._label)
        return __c

    def __int__(self):
        return self.mod

    def __call__(self, __s: str) -> str:
        return __s

    def __mul__(self, other):
        return (deepcopy(self) for _ in range(other))

class _String(_ArgLetter):
    def __init__(self):
        _ArgLetter.__init__(self)

    def __repr__(self):
        if self._label is None: self._label = consoleparser._PRINTING.TYPE_STR
        return self.mod_info_wrappers[self.mod](self._label)

class _Integer(_ArgLetter):
    def __init__(self):
        _ArgLetter.__init__(self)

    def __call__(self, __s: str) -> int | ValueError:
        return int(__s)

    def __repr__(self):
        if self._label is None: self._label = consoleparser._PRINTING.TYPE_INT
        return self.mod_info_wrappers[self.mod](self._label)

class _Float(_ArgLetter):
    def __init__(self):
        _ArgLetter.__init__(self)

    def __call__(self, __s: str) -> float | ValueError:
        return float(__s)

    def __repr__(self):
        if self._label is None: self._label = consoleparser._PRINTING.TYPE_FLOAT
        return self.mod_info_wrappers[self.mod](self._label)

class _Boolean(_ArgLetter):
    def __init__(self):
        _ArgLetter.__init__(self)

    def __call__(self, __s: str) -> bool | ValueError:
        __bool = {
            'true': True,
            'false': False,
            '1': True,
            '0': False,
            'on': True,
            'off': False
        }
        try:
            return __bool[__s.lower()]
        except KeyError:
            raise ValueError(f"must be `true' or `false': {__s!r}")

    def __repr__(self):
        if self._label is None: self._label = consoleparser._PRINTING.TYPE_BOOL
        return self.mod_info_wrappers[self.mod](self._label)

class _LiteralEval(_String):
    def __init__(self):
        _String.__init__(self)

    def __call__(self, __s: str) -> object | ValueError:
        return literal_eval(__s)

    def __repr__(self):
        if self._label is None: self._label = consoleparser._PRINTING.TYPE_LIEV
        return self.mod_info_wrappers[self.mod](self._label)

OPT = OPTIONAL = -1
EOL = TO_EOL = 2
INF = INFINIT = 3
STR = STRING = _String()
INT = INTEGER = _Integer()
FLOAT = _Float()
BOOL = BOOLEAN = _Boolean()
LIEV = LITERAL_EVAL = _LiteralEval()

OPT_STR = STR & OPT
OPT_INT = INT & OPT
OPT_FLOAT = FLOAT & OPT
OPT_BOOL = BOOL & OPT
OPT_LIEV = LIEV & OPT

STR_EOL = STR & EOL
LIEV_EOL = LIEV & EOL

OPT_STR_EOL = STR & EOL & OPT
OPT_LIEV_EOL = LIEV & EOL & OPT

STR_INF = STR & INF
INT_INF = INT & INF
FLOAT_INF = FLOAT & INF
BOOL_INF = BOOL & INF
LIEV_INF = LIEV & INF

OPT_STR_INF = STR & INF & OPT
OPT_INT_INF = INT & INF & OPT
OPT_FLOAT_INF = FLOAT & INF & OPT
OPT_BOOL_INF = BOOL & INF & OPT
OPT_LIEV_INF = LIEV & INF & OPT

