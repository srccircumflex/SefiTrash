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


from re import search
from functools import lru_cache
from os import path


PATH = path.dirname(__file__)
RGB_TABLE = PATH + "/_RGB.txt"
PATH = PATH + "/_Spectra/"


class _Spectra:

    @staticmethod
    def gray(r:int, g:int, b:int) -> bool: return r == g == b

    @staticmethod
    def light(r:int, g:int, b:int) -> bool: return r > 200 and g > 200 and b > 200

    @staticmethod
    def dark(r:int, g:int, b:int) -> bool: return r < 200 and g < 200 and b < 200

    @staticmethod
    def red(r:int, g:int, b:int) -> bool: return r > g and r > b

    @staticmethod
    def green(r:int, g:int, b:int) -> bool: return g > r and g > b

    @staticmethod
    def blue(r:int, g:int, b:int) -> bool: return b > g and b > r

    @staticmethod
    def cyan(r:int, g:int, b:int) -> bool: return (g == b and r < g) or (b > 100 and g > 100 and r < 32)

    @staticmethod
    def yellow(r:int, g:int, b:int) -> bool: return (r == g and b < r) or (r > 100 and g > 100 and b < 32)

    @staticmethod
    def magenta(r:int, g:int, b:int) -> bool: return (r == b and g < r) or (r > 100 and b > 100 and g < 32)


def _getindex() -> dict:
    _spectra = {}
    for _spectrum in _Spectra.__dict__:
        if _spectrum.startswith('_'): continue
        _spectra.setdefault(_spectrum, (PATH + _spectrum + ".txt", getattr(_Spectra, _spectrum)))
    return _spectra


def _flush() -> None:
    for _spectrum, item in _getindex().items():
        with open(item[0], "w") as f:
            f.write("")


def _find_rgb_id(ln: str, _re: str = "\w.*") -> tuple[int, int, int, str]:
    if m := search(f"^\s*(\d+)\s+(\d+)\s+(\d+)\s+({_re})(\W|$)", ln):
        return int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)


def _str_rgb_id(r, g, b, _id) -> str:
    return "%-3d %-3d %-3d    %s\n" % (r, g, b, _id)


def _categorize() -> None:
    _spectra = _getindex()
    with open(RGB_TABLE) as f:
        while ln := f.readline():
            if rgb_id := _find_rgb_id(ln):
                r, g, b, _id = rgb_id
                for _spectrum, item in _spectra.items():
                    if item[1](r, g, b):
                        with open(item[0], "a") as of:
                            of.write(_str_rgb_id(r, g, b, _id))


def spectra() -> list:
    return list(_getindex())


def spectrum(__spectrum: str) -> list:
    _spectrum = []
    with open(_getindex()[__spectrum][0]) as f:
        while ln := f.readline():
            if rgb_id := _find_rgb_id(ln):
                _spectrum.append(rgb_id[-1])
    return _spectrum


def print_lookup(__spectrum: str = None, __esc: str = "\u001b") -> None:
    _spectra = _getindex()
    if __spectrum:
        if not (_item := _spectra.get(__spectrum)):
            raise LookupError(__spectrum)
        _spectra = {__spectrum: _item}
    for __spectrum, item in _spectra.items():
        print("\n\n", __spectrum, " : \n")
        with open(item[0]) as f:
            _ln = ""
            while ln := f.readline():
                if rgb_id := _find_rgb_id(ln):
                    _ln += f"{__esc}[48;2;%d;%d;%dm                {__esc}[0m%-18s" % rgb_id
                    if len(_ln) > 120:
                        print(_ln)
                        _ln = ""
            print(_ln)


@lru_cache()
def _get(color: str) -> str:
    """
    :return: "2;r;g;b;"
    """
    with open(RGB_TABLE) as f:
        while ln := f.readline():
            if rgb_id := _find_rgb_id(ln, color):
                r, g, b, _ = rgb_id
                return "2;%d;%d;%d;" % (r, g, b)
        raise LookupError(color)

def foreground(color: str) -> str:
    """
    :return: "38;2;r;g;b;"
    """
    if rgb := _get(color):
        return "38;" + rgb

def background(color: str) -> str:
    """
    :return: "48;2;r;g;b;"
    """
    if rgb := _get(color):
        return "48;" + rgb


def hascolor(color: str, __lookup: bool = False, __esc: str = "\u001b") -> bool:
    try:
        if rgb := _get(color)[:-1]:
            if __lookup:
                print(*rgb.split(';')[1:], ':')
                print(f"{__esc}[48;{rgb}m" + "\n" * 8, f"{__esc}[0m")
            return True
    except LookupError:
        return False


fg: foreground = foreground
bg: background = background

default_foreground = default_fg = "39;"
default_background = default_bg = "49;"

red_fg = fg("red")
green_fg = fg("green")
blue_fg = fg("blue")
yellow_fg = fg("yellow")
cyan_fg = fg("cyan")
magenta_fg = fg("magenta")
black_fg = fg("black")
white_fg = fg("white")

red_bg = bg("red")
green_bg = bg("green")
blue_bg = bg("blue")
yellow_bg = bg("yellow")
cyan_bg = bg("cyan")
magenta_bg = bg("magenta")
black_bg = bg("black")
white_bg = bg("white")

red_relfg = "31;"
green_relfg = "32;"
blue_relfg = "34;"
yellow_relfg = "33;"
cyan_relfg = "36;"
magenta_relfg = "35;"
black_relfg = "30;"
white_relfg = "37;"

red_relbg = "41;"
green_relbg = "42;"
blue_relbg = "44;"
yellow_relbg = "43;"
cyan_relbg = "46;"
magenta_relbg = "45;"
black_relbg = "40;"
white_relbg = "47;"

class _Support:
    default_underline = default_ul = "59;"

    @staticmethod
    def underline(color: str) -> str:
        """
        :return: "58;2;r;g;b;"
        """
        if rgb := _get(color):
            return "58;" + rgb

SupportKitty = _Support
SupportVTE = _Support
SupportMintty = _Support
SupportITerm2 = _Support
