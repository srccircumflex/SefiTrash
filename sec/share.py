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


from socket import socket, AF_INET, SOCK_DGRAM
from re import search, sub, Match
from sys import getfilesystemencoding
from typing import Iterable


class DefIfEndIf:
    def __init__(self, file, ifdef:bytes, endif:bytes, comnt:bytes):
        self.ifdef = ifdef.replace(b' ', b'')
        self.endif = endif.replace(b' ', b'')
        ifdef = b'\n' + self.ifdef
        endif = b'\n' + self.endif
        self.comnt = comnt
        self.file = file
        self.configured: bool = False
        try:
            with open(file, "rb") as f:
                file = f.read().replace(b' ', b'')
                if search(b"(\A|\n)" + self.ifdef, file) and not search(b"\n" + self.endif, file):
                    raise SyntaxError(rf"etc:{self.file} <{ifdef} without {endif}>")
                if search(b"\n" + self.endif, file) and not search(b"(\A|\n)" + self.ifdef, file):
                    raise SyntaxError(rf"etc:{self.file} <{endif} without {ifdef}>")
                if search(b"(\A|\n)" + self.ifdef, file) and search(b"\n" + self.endif, file):
                    self.configured = True
        except FileNotFoundError:
            pass

    def read_rc(self):
        assert self.configured, 'read_rc: read on UnDefinition'
        ifdef = False
        with open(self.file, "rb") as f:
            while True:
                ln = f.readline()
                if ln == b'\n': continue
                _ln = ln.replace(b' ', b'')
                if not ifdef and not (ifdef := _ln.startswith(self.ifdef)): continue
                if _ln.startswith(self.endif): return
                if _ln.startswith(self.comnt): continue
                yield ln

    def insert_rc(self):
        assert self.configured, 'insert_rc: insert at UnDefinition'
        ifdef = False
        pre_lines = b''
        with open(self.file, "rb") as f:
            while True:
                ln = f.readline()
                if ln == b'\n':
                    pre_lines += ln
                    continue
                _ln = ln.replace(b' ', b'')
                if not ifdef and not (ifdef := _ln.startswith(self.ifdef)):
                    pre_lines += ln
                    continue
                pre_lines += ln
                break
            while not (ln := f.readline()).replace(b' ', b'').startswith(self.endif):
                pass
            end_lines = ln + f.read()
        with open(self.file, "wb") as f:
            f.write(pre_lines)
            while True:
                ln = yield
                if ln is None:
                    f.write(end_lines)
                    return
                f.write(ln)

    def insert_rc_all_(self, *args, encoding=getfilesystemencoding()):
        insert_rc = self.insert_rc()
        next(insert_rc)
        for ln in args:
            if not isinstance(ln, bytes):
                ln = ln.encode(encoding)
            insert_rc.send(ln)
        try:
            insert_rc.send(None)
        except StopIteration:
            pass


class LineFinder:
    def __init__(self, file: str, attrs: Iterable):
        self._last_index = 0
        self.present_lines: list[tuple[int, Match, str]] = list()
        self.file = file
        with open(file) as file:
            file = "\n" + file.read()
            self.lines = file.splitlines(True)
        for n, line in enumerate(self.lines):
            for _attr in attrs:
                if m := search("^" + _attr + "(\W.*|$)", line):
                    a = search("\w+", m.group()).group()
                    self.present_lines.append((n, m, a))

    def overwrite_line_(self, n: int, ln: str):
        self.lines[n] = ln + ("\n" if ln else "")
        if n > self._last_index:
            self._last_index = n
        return self

    def insert_remaining(self, ln: str):
        self.lines.insert(self._last_index, ln + "\n")
        return self

    def insert_before(self, ln: str):
        self.lines.insert(self.present_lines[0][0], ln + "\n")
        return self

    def insert_after(self, ln: str):
        self.lines.insert(self.present_lines[-1][0] + 1, ln + "\n")
        return self

    def write_out(self):
        with open(self.file, "w") as f:
            f.write(str().join(self.lines).strip())
        return self

    def flush(self):
        for m in self.present_lines:
            self.overwrite_line_(m[0], "")
        return self

    def final_insert(self, ln):
        if self.present_lines:
            self.overwrite_line_(self.present_lines.pop(0)[0], ln)
        else:
            self.insert_remaining(ln)
        self.flush()
        return self

    def print_present(self):
        for m in self.present_lines:
            print(m[1].group())
        return self


def getpublicip():
    from urllib.request import Request, urlopen
    return urlopen(Request("http://www.ifconfig.me")).read().decode('utf8')


def getlocalip(DNS:str="8.8.8.8"):
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.connect((DNS, 80))
            return s.getsockname()[0]
        finally:
            s.close()


def subwinpath(path: str):
    return sub(":/?", ":/", sub("\\\+", "/", path))
