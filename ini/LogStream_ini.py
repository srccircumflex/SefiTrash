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

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import time

from _rc._run import configurations as CNF

from sec.Loggers import LOGS_


class Inspect:
    def __init__(self):
        if not CNF.INSPECT_BINDING:
            LOGS_.blackbox.logg(40, "[[ E ]] not provided")
            CNF.EXP_EXIT(1)
        self.jsock = socket(AF_INET, SOCK_STREAM)
        self.jsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.con = CNF.INSPECT_BINDING

    def jread(self):
        try:
            self.jsock.connect(self.con)
        except ConnectionError as err:
            LOGS_.blackbox.logg(40, err)
            return

        LOGS_.blackbox.logg(25, CNF.STRINGS.INSPECTTRM_CON % CNF.INSPECT_BINDING, ico=CNF.PRINT_ICOS.mail)

        while True:
            try:
                dat = self.jsock.recv(256)
                if not dat: raise EOFError
                print(dat.decode(CNF.LOG_ENC, errors="replace"), end='', flush=True)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                self.jsock.close()
                exit('')
            except ConnectionError as err:
                LOGS_.blackbox.logg(40, err)
                break
        self.jsock.close()


_c = 0
_t = time()

def main():
    global _t, _c
    while True:
        j = Inspect()
        j.jread()
        if not CNF.MOD_STREAM_READLOOP: break
        _c += 1
        if _c > 2:
            if (t := time()) - _t < 1: break
            _c = 0
            _t = t
