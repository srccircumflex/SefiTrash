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


import ansilib
from ._parser import ConsoleParser
from . import _exceptions as Exceptions


class AnsiArgs:
    CMD = (ansilib.SGRAttr.bold,)
    N_OPTS_FROM = (ansilib.SGRAttr.underline,)
    N_OPTS_TO = (ansilib.SGRAttr.underline,)
    FUNC = (ansilib.Colors.fg("yellow2"),)
    DEFAULT_OPTION = (ansilib.SGRAttr.bold,)
    SQAREBR_LEFT = (ansilib.SGRAttr.bold,)
    SQAREBR_RIGHT = (ansilib.SGRAttr.bold,)
    INF_POINTS = (ansilib.SGRAttr.bold,)
    EOL_SHIFT = (ansilib.SGRAttr.bold,)
    STR = (ansilib.Colors.green_fg,)
    INT = (ansilib.Colors.cyan_fg,)
    FLOAT = (ansilib.Colors.cyan_fg,)
    BOOL = (ansilib.Colors.blue_fg,)
    LIEV = (ansilib.Colors.yellow_fg,)
    EXEPTION = (ansilib.Colors.red_fg, ansilib.SGRAttr.bold)
    INTERCEPT = (ansilib.SGRAttr.bold,)
    OR = (ansilib.Colors.fg("orange2"),)


MANUAL_PAGES_FILE: str = None
MANUAL_PAGES_GZIP: bool = False

ANSI_LOOKUP: bool = True
ANSI_RAISE_ERROR: bool = False
ANSI_IGNORE_ERROR: bool = False

LOOKUP_FUNC: bool = True
LOOKUP_INTERCEPT: bool = True


class _PRINTING:
    FUNC_MAIN = "  _>%s"
    CMD_HEADER = "%(cmd)-8s %(from)d %(to_opts)d  ->%(func)s"
    OPTION = "    %-8s"
    DEFAULT_OPTION = " >  %-8s"
    ARG = " %s"
    CMD = "%-12s"
    CMD_LOOK_LN_MAX_CARS = 48
    MOD_WRAPPER_INF_OPTIONAL = "[%s...]"
    MOD_WRAPPER_EOL_OPTIONAL = "[%s<<]"
    MOD_WRAPPER_OPTIONAL = "[%s]"
    MOD_WRAPPER = "%s"
    MOD_WRAPPER_EOL = "%s<<"
    MOD_WRAPPER_INF = "%s..."
    TYPE_STR = "str"
    TYPE_INT = "int"
    TYPE_FLOAT = "float"
    TYPE_BOOL = "bool"
    TYPE_LIEV = "liev"
    EXP = "[!] %s\n"
    INTERCEPT = " ^>%(func)s"
    OR = "|"

    def __init__(self):
        self._SGR = (ansilib.SGRInstance if ansilib.SGRInstance else
                     ansilib.SelectGraphicRendition(
                         _disabled=ANSI_LOOKUP ^ True,
                         raise_initerr=ANSI_RAISE_ERROR,
                         ignore_initerr=ANSI_IGNORE_ERROR
                     ))
        _cmd = self._SGR.wrap(
            "%-8s", *AnsiArgs.CMD
        )
        _from = self._SGR.wrap(
            "%d", *AnsiArgs.N_OPTS_FROM
        )
        _to = self._SGR.wrap(
            "%d", *AnsiArgs.N_OPTS_TO
        )
        _func = self._SGR.wrap(
            "%s", *AnsiArgs.FUNC
        )
        self.FUNC_MAIN = "  _>%s" % _func
        self.CMD_HEADER = "%s %s %s %%s" % (_cmd, _from, _to)
        self.OPTION = "    %-8s"
        self.DEFAULT_OPTION = self._SGR.wrap(" >  %-8s", *AnsiArgs.DEFAULT_OPTION)
        self.ARG = " %s"
        self.CMD = "%-12s"
        self.CMD_LOOK_LN_MAX_CARS = 48
        sb_left = self._SGR.wrap('[', *AnsiArgs.SQAREBR_LEFT)
        sb_right = self._SGR.wrap(']', *AnsiArgs.SQAREBR_RIGHT)
        points = self._SGR.wrap('...', *AnsiArgs.INF_POINTS)
        arrow = self._SGR.wrap('<<', *AnsiArgs.EOL_SHIFT)
        self.MOD_WRAPPER_INF_OPTIONAL = "%s%%s%s%s" % (sb_left, points, sb_right)
        self.MOD_WRAPPER_EOL_OPTIONAL = "%s%%s%s%s" % (sb_left, arrow, sb_right)
        self.MOD_WRAPPER_OPTIONAL = "%s%%s%s" % (sb_left, sb_right)
        self.MOD_WRAPPER = "%s"
        self.MOD_WRAPPER_EOL = "%%s%s" % arrow
        self.MOD_WRAPPER_INF = "%%s%s" % points
        self.TYPE_STR = self._SGR.wrap("str", *AnsiArgs.STR)
        self.TYPE_INT = self._SGR.wrap("int", *AnsiArgs.INT)
        self.TYPE_FLOAT = self._SGR.wrap("float", *AnsiArgs.FLOAT)
        self.TYPE_BOOL = self._SGR.wrap("bool", *AnsiArgs.BOOL)
        self.TYPE_LIEV = self._SGR.wrap("liev", *AnsiArgs.LIEV)
        self.EXP = self._SGR.wrap("[!]", *AnsiArgs.EXEPTION) + " %s\n"
        self.INTERCEPT = " %s%s" % (self._SGR.wrap("^>", *AnsiArgs.INTERCEPT), _func)
        self.OR = self._SGR.wrap("|", *AnsiArgs.OR)


def _write_info_sheet(parser: ConsoleParser):
    out = "ConsoleParserInfo.txt"
    with open(out, "w") as f:
        for command, config in parser.config.items():
            f.write("$$$%%(%s)\n\n" % (command,))
            for opt in config[1][list(config[1])[0]].keys():
                if opt:
                    f.write("  $$%%(%s)\n\n" % opt)
        f.write("\n\n\n$$$%(EOF)")
    print(f"[o] {out}")


def _write_config(parser: ConsoleParser):
    out = "ConsoleParserConfig.py"
    with open(out, "w") as f:
        f.write('from consoleparser import argletters\n\nCONFIG = {\n')
        for command, config in parser.config.items():
            n_o = parser._nopts_from_command(command)
            fun = ("None,  # <none function>" if config[0] == parser._snake_func else f"# {config[0]},")
            f.write(f"\t{command!r}: (\n\t\t{fun}\n\t\t" + "{\n" + f"\t\t\t{n_o}: " + "{\n")
            for opt, letters in parser._get_setsbox_conf(command)[1].items():
                f.write(f"\t\t\t\t{opt!r}: ")
                if letters == 0:
                    f.write("(0,),\n")
                    continue
                if not isinstance(letters, (tuple, list, set)):
                    letters = (letters,)
                f.write('(')
                for letter in letters:
                    f.write(letter.__config__() + ',')
                f.write('),\n')
            f.write("\t\t\t\t}")
            if None in config[1]:
                f.write(f",\n\t\t\tNone: {config[1][None]!r}")
            f.write("\n\t\t}\n\t),\n")
        f.write('}')
    print(f"[o] {out}")
