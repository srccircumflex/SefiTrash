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

from _rc import configurations as configuration_sheet
from _rc import _defaults_ as default_values
from sec.fTools import DefIfEndIf as DefIfEndIf

hasattr(default_values, '__file__')
hasattr(DefIfEndIf, '__file__')

value_name2default_name = lambda name: name.lower()
default_name2value_name = lambda name: name.upper()

from re import Pattern, compile
value_name_re: Pattern = compile("^[A-Z0-9_]+")

IFDEFENDIF: dict[str: tuple[bytes, bytes, bytes]] = {}
ifdefendif_attr: str = "IFDEFENDIF"
if hasattr(configuration_sheet, ifdefendif_attr):
    IFDEFENDIF = getattr(configuration_sheet, ifdefendif_attr)


from sys import argv
if not argv[0].endswith("-cli.py"):
    from tkinter import Tk
    ROOT_TK = Tk()
    ROOT_TK.title("SefiTrash - CnfGui")

from sys import getdefaultencoding
ROOT_DIR = __path__[0]
ENCODING = getdefaultencoding()

files_config_file = "_rc/etc/files.conf"
files_config_file = ROOT_DIR + "/" + files_config_file

MOD_DEBUG = False
