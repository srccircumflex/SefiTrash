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
from time import sleep

from _rc._run import configurations as CNF

from sec.Loggers import LOGS_


class Shelf:

    _logslvto = ('to%d', b'LOGS_._allSLVsto(%d)')
    _logflvto = ('to%d', b'LOGS_._allFLVsto(%d)')
    _logsocklvto = ('to%d', b'CNF.MOD_BGSTREAM = True; LOGS_._setSockstream(%d)')
    _rcout = {
        'l_sock': b'pprint(self.l_sock.__dict__, stream=%s)',
        'gateway_qq': b'pprint(self.gateway_qq.__dict__, stream=%s)',
        'gateway_qs': b'pprint(self.gateway_qq.__dict__, stream=%s)',
        'log': b'for log in LOGS_.__dict__: pprint(LOGS_.__dict__[log].__dict__["_log"].__dict__, stream=%s)',
        'CNF': b'pprint(CNF.__dict__, stream=%s)',
    }
    class idle:
        t10 = b'CNF.LISTEN_TIMEOUT = 10'
        t30 = b'CNF.LISTEN_TIMEOUT = 30'
        t60 = b'CNF.LISTEN_TIMEOUT = 60'
    class mailalert:
        class enable:
            login = b'CNF.MOD_LOGIN_TO_ALERT = True'
            blackbox = b'LOGS_.blackbox.handler_M.setLevel(61)'
            firewall = b'LOGS_.firewall.handler_m.setLevel(55)'
            all = b'%b;%b;%b' % (login, blackbox, firewall)
        class disable:
            login = b'CNF.MOD_LOGIN_TO_ALERT = False'
            blackbox = b'LOGS_.blackbox.handler_M.setLevel(100)'
            firewall = b'LOGS_.firewall.handler_m.setLevel(100)'
            all = b'%b;%b;%b' % (login, blackbox, firewall)
    class log:
        blackbox = b'LOGS_._enableBlackbox()'
        debug = b'LOGS_._setLVstoDebug()'
        reset = b'LOGS_._resetCNFLV()'
        sock = b'CNF.MOD_BGSTREAM = True; LOGS_._setSockstream()'
        io = b'LOGS_._resetIOStream()'
        class setlv:
            class streams:
                pass
            class files:
                pass
            class socks:
                pass
    class rc:
        terminal__output__stream__: None = ''
        class stderr:
            pass
        class socks:
            pass
    class remote:
        shutdown = b'self.gateway_qs.pipe_in.put(pf.shutdown)'
        resetf = b'self.gateway_qs.pipe_in.put(pf.reset % b"f")'
        resetF = b'self.gateway_qs.pipe_in.put(pf.reset % b"F")'


for _lv in range(0, 61, 5):
    setattr(Shelf.log.setlv.streams, Shelf._logslvto[0] % _lv, Shelf._logslvto[1] % _lv)
    setattr(Shelf.log.setlv.files, Shelf._logflvto[0] % _lv, Shelf._logflvto[1] % _lv)
    setattr(Shelf.log.setlv.socks, Shelf._logsocklvto[0] % _lv, Shelf._logsocklvto[1] % _lv)
for _attr in Shelf._rcout:
    setattr(Shelf.rc.stderr, _attr, Shelf._rcout[_attr] % b'stderr')
    setattr(Shelf.rc.socks, _attr, Shelf._rcout[_attr] % b'LOGS_._sockstream')


def get_attr(ln):
    if not ln: return Shelf
    _sub_attr = Shelf
    for _attr in ln.decode(CNF.LOC_ENC).split('.'):
        if hasattr(_sub_attr, _attr):
            _sub_attr = getattr(_sub_attr, _attr)
    if _sub_attr != Shelf:
        return _sub_attr
    print(f"nothing fount for '{ln}'")
    return False


def registry(ln):
    if _attr := get_attr(ln):
        if hasattr(_attr, "__dict__"):
            for _at in _attr.__dict__:
                if _at.startswith('_'): continue
                print("%(attr)-10s : %(val)s" % {'attr': _at,'val': _attr.__dict__[_at]})
        else: print(f"'{_attr}' has no attr '__dict__'")
    else: print(f"no entry for '{ln}'")


def _help():
    print(
        "PREFIXES\n"
        "  /[<obj.obj ...>]        search prefabricated strings\n"
        "  *<obj[.obj ...].val>    use prefabricated string\n"
        "\n"
        "exit       exiting"
    )
    pass


class Intervention:
    def __init__(self):
        if not CNF.INTERVENT_BINDING:
            LOGS_.blackbox.logg(40, "[[ E ]] not provided")
            CNF.EXP_EXIT(1)
        self.jsock = socket(AF_INET, SOCK_STREAM)
        self.jsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.con = CNF.INTERVENT_BINDING

    def jwrite(self):

        LOGS_.blackbox.logg(25, CNF.STRINGS.INTERVENT_CON % CNF.INTERVENT_BINDING, ico=CNF.PRINT_ICOS.intercon)

        while True:
            try:
                self.jsock = socket(AF_INET, SOCK_STREAM)
                self.jsock.connect(self.con)
                while True:
                    try:
                        dat = input("]<<- ").encode(CNF.LOC_ENC)
                        if dat == b'help':
                            _help()
                            continue
                        if dat.startswith(b'/'):
                            registry(dat[1:])
                            continue
                        if dat.startswith(b'*'):
                            dat = get_attr(dat[1:])
                        if dat in (b'exit', b'done', b'0', b'quit', b'x'): raise EOFError
                        if not dat: continue
                        self.jsock.sendall(dat)
                        break
                    except KeyboardInterrupt:
                        print('')
                self.jsock.close()
                sleep(.2)
            except EOFError:
                print("^D")
                self.jsock.close()
                break
            except ConnectionError as err:
                LOGS_.blackbox.logg(40, err)
                self.jsock.close()
                CNF.EXP_EXIT(1)


def main():
    Intervention().jwrite()
