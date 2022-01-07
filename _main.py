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
from re import sub as _re_sub
from ast import literal_eval

if (len(argv) - 1) % 2:
    if "--help" in argv[-1]:
        raise NotImplementedError
    if "-h" in argv[-1]:
        raise NotImplementedError
    if "help" in argv[-1]:
        raise NotImplementedError
if __name__ == "__main__":
    raise NotImplementedError

if _sys_platform == "win32":
    sys_path.append(_re_sub("\\\[^\\\]+$", "", __file__))
else:
    sys_path.append(_re_sub("/[^/]+$", "", __file__))


from _rc import configurations as CNF

def set_argv(raise_NoConfigurationAttribute: bool = True):
    try:
        for _ in range(1, len(argv), 2):
            attr = argv.pop(1)
            if hasattr(CNF, attr.upper()):
                val = argv.pop(1)
                print(f"SET: {attr.upper()} = {val}")
                setattr(CNF, attr.upper(), literal_eval(val))
            elif raise_NoConfigurationAttribute:
                raise AttributeError(f"NoConfigurationAttribute : {attr}")
            else:
                argv.insert(1, attr)
                break
    except (SyntaxError, ValueError) as e:
        print(" something went wrong ... \n"
              " remember to wrap quotes like '\"<str>\"' for string definitions")
        exit(" ! {} in {!r}".format(type(e), val))
    except AttributeError as e:
        exit(" ! {}".format(e))
    except IndexError:
        exit(" ! {} expects a value".format(attr))


if argv[0].endswith('Bypass.py'):
    set_argv(False)
else:
    set_argv()
