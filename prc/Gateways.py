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

from queue import Queue
from _queue import Empty
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

from _rc import configurations as CNF

from sec.Loggers import LOGS_
from sec.PermCTL import SecureCall
from sec.Proto import StreamHeader, ParseStreamHeader, pm, resp
from prc.Bridge import Bridge


class GateWayQQ(Thread, Bridge, SecureCall):

    pipe_lock = False

    def __init__(self, pipe_in:Queue, pipe_out:Queue, client_cache:dict, intercept_methods_update:dict=None):
        Thread.__init__(self)
        Bridge.__init__(self, pipe_in, pipe_out, client_cache)
        SecureCall.__init__(self, {(list(client_cache)[0], None)})
        self._client_cache = client_cache
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out
        self.header = None
        self.intercept_methods = {
            pm._w_conf: self._write_conf,
            pm._close_gateway: self._gw_close,
            pm._login_pong: self._bend,
            pm._bend : self._bend,
            pm._ierr : self._put_response
        }

        if intercept_methods_update:
            self.intercept_methods |= intercept_methods_update

        self.keep_alive = True
        self.user = client_cache[list(client_cache)[0]][2]
        if self.user is None:
            self.config_files = {'H': CNF.AUTH_CONF[None]['hst'], 'P': CNF.AUTH_CONF[None]['spc']}
        LOGS_.bridge.logg(25, CNF.STRINGS.BRIDGE % client_cache, ico=CNF.PRINT_ICOS.bridge_on)

    def _put_response(self, res=None): self.pipe_out.put(
        resp.get_response(res) if res else resp.get_response(self.header.header)
    )

    def _write_conf(self):
        with open(self.config_files[self.header.option_liev["T"]], 'wb') as f:
            for _ in CNF.BUFFER_ITER(self.header.option_liev["l"]):
                f.write(self.pipe_in.get())

    def _bend(self):
        if self.header.method == pm._bend:
            self.pipe_out.put(self.header.option)
            _header = ParseStreamHeader(self.header.option)
            try:
                length = _header.option_liev.get("l")
                if length:
                    self.pipe_out.put(self.pipe_in.get())
            except (AttributeError, KeyError):
                pass
        else:
            self.pipe_out.put(self.header.header)

    def _gw_close(self) -> None:
        self.pipe_out.put(self.header.option)
        self.pipe_out.put(None)
        self.keep_alive = False

    def run(self):
        while self.keep_alive:

            self.pipe_lock = False
            _header = self.pipe_in.get()
            self.pipe_lock = True

            self.header = (_header if isinstance(_header, StreamHeader) else ParseStreamHeader(_header))

            intercept = self.intercept_methods.get(self.header.method)
            if intercept:
                try:
                    self.call(self.header, intercept)
                except PermissionError:
                    self._put_response(resp.rRES(resp.CODEs.Unauthorized))
                    if self.header.option_json:
                        try:
                            if _l := self.header.option_json.get('l'):
                                for _ in CNF.BUFFER_ITER(_l): self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT)
                            for stack in range(1, CNF.DAT_MAX_STACKS + 1):
                                if _l := self.header.option_json.get('l%d' % stack):
                                    for _ in CNF.BUFFER_ITER(_l): self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT)
                                else:
                                    break
                        except Empty: pass
                continue

            if self.header.method:
                m_ = '_do_' + self.header.method.decode(CNF.SRM_ENC)
                pre_ = '_pre_' + self.header.method.decode(CNF.SRM_ENC)
                if hasattr(self, pre_):
                    self._put_response(res=getattr(self, pre_))
                if not hasattr(self, m_):
                    self.header.header = resp.iEXP(resp.CODEs.NotImplementError, self.header)
                    self._put_response()
                else:
                    _attr = getattr(self, m_)
                    try:
                        res = self.call(self.header, _attr)
                    except PermissionError:
                        res = resp.rRES(resp.CODEs.Unauthorized)
                        if self.header.option_json:
                            try:
                                if _l := self.header.option_json.get('l'):
                                    for _ in CNF.BUFFER_ITER(_l): self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT)
                                for stack in range(1, CNF.DAT_MAX_STACKS + 1):
                                    if _l := self.header.option_json.get('l%d' % stack):
                                        for _ in CNF.BUFFER_ITER(_l): self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT)
                                    else:
                                        break
                            except Empty: pass
                    if res: self._put_response(res=res)

        LOGS_.bridge.logg(25, CNF.STRINGS.BRIDGE_CLOSED, ico=CNF.PRINT_ICOS.bridge_off)


class GateWayQS(Thread):

    def __init__(self, connect:tuple, _quiet:bool=False):
        Thread.__init__(self)
        self.pipe_in = Queue(200)
        self.connect = connect
        self.keep_alive = True
        self._q = _quiet

    def run(self) -> None:
        if not self._q: LOGS_.sockio.logg(25, CNF.STRINGS.SENDER_ON, ico=CNF.PRINT_ICOS.on)
        with socket(AF_INET, SOCK_STREAM) as sock_:
            with CNF._SSL_CONT_SENDER.wrap_socket(sock_, server_hostname=CNF.IP_LOCAL) as S_sock:
                while self.keep_alive:
                    try:
                        S_sock.connect(self.connect)
                        LOGS_.sockio.logg(25, CNF.STRINGS.SENDER_CON % str(self.connect), ico=CNF.PRINT_ICOS.o_pipe)
                        while True:
                            data = self.pipe_in.get()
                            if data is None:
                                sleep(CNF.CONRESET_TIMEOUT)
                                return
                            S_sock.sendall(data)
                            LOGS_.sockio.logg(5, data)
                    except OSError as e:
                        if not self._q:
                            LOGS_.sockio.logg(10, type(e), e, mt=self.run, ico=CNF.PRINT_ICOS.broken_pipe)
                        if e.errno in (32, 104, 110, 111):  # BrokenPipe, ResetByPear, ConnectionTimeOut, Refused
                            raise ConnectionResetError
                        LOGS_.blackbox.logg(60, type(e), e, mt=self.run, ico=CNF.PRINT_ICOS.broken_pipe)
                    finally:
                        while not self.pipe_in.empty(): self.pipe_in.get()
                        break
                if not self._q: LOGS_.sockio.logg(25, CNF.STRINGS.SENDER_OFF, ico=CNF.PRINT_ICOS.standby)
