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


from sys import path as sys_path
from os import path

sys_path.insert(0, path.dirname(__file__))

from _rc import configurations as CNF
import _main
hasattr(_main, "__file__")

CNF.CLIENT_SIDE = True

from ini.Client_ini import main
try:
    from ini.Client_ini import main
except Exception as e:
    print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
    CNF.EXP_EXIT(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit('')
    except Exception as e:
        print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
        CNF.EXP_EXIT(1)
