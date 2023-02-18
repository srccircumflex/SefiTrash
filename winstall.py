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


from re import sub as _re_sub
from sys import platform

if __name__ == "__main__":

    if platform != "win32":
        raise NotImplementedError(f"{platform=}")

    try:

        MAIN_ROOT = _re_sub("\\\[^\\\]+$", "", __file__) + '/'

        MAIN_FILES = [
            MAIN_ROOT + "Host.py",
            MAIN_ROOT + "Client.py",
            MAIN_ROOT + "Bypass.py",
            MAIN_ROOT + "LogStream.py",
            MAIN_ROOT + "Intervene.py",
            MAIN_ROOT + "Config-tk.py",
            MAIN_ROOT + "Config-cli.py",
        ]

        for f in MAIN_FILES:
            print(f"## remove SHEBANG from {f}")
            with open(f, "r") as _f:
                _r = _f.read()
            with open(f, "w") as _f:
                _f.write(_re_sub("\A#! /usr/bin/python3\.9", "#", _r))

    except Exception as e:
        print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
        input("[1]-")
