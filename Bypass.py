#! /usr/bin/python3.9
#
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


from sys import argv
from sys import path as sys_path
from sys import platform as _sys_platform
from re import sub, search


if _sys_platform == "win32":
    sys_path.append(sub("\\\[^\\\]+$", "", __file__))
else:
    sys_path.append(sub("/[^/]+$", "", __file__))

from _rc import configurations as CNF
import _main
hasattr(_main, "__file__")

CNF.CLIENT_SIDE = True
CNF.LATERAL_ = True

from _rc._run import configurations as CNF

try:
    from sec.Bypass import ByPassj
except Exception as e:
    print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
    CNF.EXP_EXIT(1)

if __name__ == "__main__":
    try:
        j = ByPassj(True)
        if len(argv) > 1:
            j.write("".join([sub(" ", "\\ ", i) + " " for i in argv[1:]]))
        else:
            j.write(input("]<<- "))
        resp = j.read()
        rcod = search("(?<=\[)\d*(?=]$)", resp).group()
        resp = sub("\[\d*]$", "", resp)
        print(resp, end="")
        if rcod:
            exit(int(rcod))
        exit(0)
    except KeyboardInterrupt:
        exit('')
    except Exception as e:
        print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
        CNF.EXP_EXIT(1)
