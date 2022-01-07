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



from time import sleep
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout

from sys import stderr, stdout
from pprint import pprint
from sec.Proto import pf

from _rc import configurations as CNF

from sec.Loggers import LOGS_


class InterventionEXEC:

    def __init__(self):
        self.enabled = CNF.INTERVENT_BINDING
        if self.enabled:
            self.jsock = socket(AF_INET, SOCK_STREAM)
            self.jsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.jsock.bind(CNF.INTERVENT_BINDING)
            self.jsock.setblocking(False)
            self.jsock.settimeout(.2)
            self.jsock.listen(1)
            LOGS_.blackbox.logg(25, CNF.STRINGS.INTERVENT_AT % CNF.INTERVENT_BINDING, ico=CNF.PRINT_ICOS.interpro)

    def jread(self):
        if not self.enabled: return
        data = b''
        try:
            con, adr = self.jsock.accept()
            print(CNF.PRINT_INTERVENTION_ONOFF[1], end='', flush=True, file=(LOGS_._sockstream if CNF.MOD_BGSTREAM else stderr))
            while True:
                dat = con.recv(1024)
                if not dat: break
                data += dat
            exec(data)
            for fls in CNF.PRINT_INTERVENTION_FLUSH:
                print(fls, end='', flush=True, file=(LOGS_._sockstream if CNF.MOD_BGSTREAM else stderr))
                sleep(.2)
        except timeout:
            return
        except OSError as e:
            if e.errno != 11:
                print(CNF.PRINT_INTERVENTION_ERROR % f"{type(e)} {e}", flush=True, file=(LOGS_._sockstream if CNF.MOD_BGSTREAM else stderr))
        except Exception as e:
            print(CNF.PRINT_INTERVENTION_ERROR % f"{type(e)} {e}", flush=True, file=(LOGS_._sockstream if CNF.MOD_BGSTREAM else stderr))
        finally:
            print(CNF.PRINT_INTERVENTION_ONOFF[0], end='', flush=True, file=(LOGS_._sockstream if CNF.MOD_BGSTREAM else stderr))


class ByPassj:
    def __init__(self, cli=False):
        self.name = "<ByPass>"
        self.jsock = socket(AF_INET, SOCK_STREAM)
        self.jsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        if cli:
            self.recsock = (CNF.BYPASS_CLI_IP, CNF.BYPASS_CLI_PORT)
            self.sedsock = (CNF.BYPASS_IP, CNF.BYPASS_PORT)
        else:
            self.recsock = (CNF.BYPASS_IP, CNF.BYPASS_PORT)
            self.sedsock = (CNF.BYPASS_CLI_IP, CNF.BYPASS_CLI_PORT)
        self.jsock.bind(self.recsock)
        self.jsock.listen(1)
        self.eof = 0

    def read(self):
        dats = ""
        _s, _ = self.jsock.accept()
        while True:
            dat = _s.recv(64).decode(CNF.SRM_ENC, errors="replace")
            dats += dat
            if not dat: return dats

    def flush(self, *args, **kwargs) -> None: pass

    def write(self, dat):
        with socket(AF_INET, SOCK_STREAM) as sock:
            try:
                sock.connect(self.sedsock)
                sock.sendall(dat.encode(CNF.SRM_ENC, errors="replace"))
            except ConnectionRefusedError: return
