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
from threading import Thread
from os import getpid, kill
from time import sleep
from queue import Queue
from sys import argv

from _rc import configurations as CNF

from sec.Proto import StreamHeader, pm, pf, resp
from prc.Gateways import GateWayQS
from sec.PermCTL import Verification, SecureCall
from sec.Loggers import LOGS_
from sec.fTools import exp_full_trace


class SockPort(Thread, Verification, SecureCall):

    def __init__(self, port_range:tuple, local_address:str):
        Thread.__init__(self)
        Verification.__init__(self)
        SecureCall.__init__(self, self.client_set)
        self.StreamHeader = StreamHeader
        self.port_range = port_range
        self.local_address = local_address
        self.local_port: int = int()
        self.sock = None
        self.pipe_out = Queue(200)
        self.header = None
        self.intercept_methods = {
            pm._shutdown: self.ls_shutdown,
            pm._port_ping: self.port_pong,
            pm._port_pong: self.port_handshake,
            pm._login_ping: self.login_pong,
            pm._login_pong: self.login_handshake,
            pm._do_login_change: self.login_change,
            pm._w_conf: self.__bend,
            pm._do_reset: self.reset_,
            pm._pick : self._stone,
            pm._kill : self.t_kill,
            pm._pair : self.pairing
        }
        self.keep_alive = True

    # //202// {"T": ""//x// {"u":"user","i":'h3xd1'} ///""|"H"|"P"} ///
    def pairing(self, *_, **__):
        options = self.header.option_liev
        if options.get("T") in ('H', 'P'):
            self.__bend(_un_verified=True)
            self.pipe_out.get()
            self.solve_paring(options, self.pipe_out)
        else:
            configs = self.get_paring(options)
            if configs:
                gw = GateWayQS((self.client_ip, self.received_port))
                gw.pipe_in.put(pf.pair % (b'P', len(configs[0])))
                gw.pipe_in.put(configs[0])
                gw.pipe_in.put(None)
                gw.run()
                gw = GateWayQS((self.client_ip, self.received_port))
                gw.pipe_in.put(pf.pair % (b'H', len(configs[1])))
                gw.pipe_in.put(configs[1])
                gw.pipe_in.put(None)
                gw.run()
            raise ConnectionResetError

    # //001// 1111 ///  ->  //010// 1111 ///
    def port_pong(self, *_, **__):
        self.received_port = self.header.option_int
        gw = GateWayQS((self.client_ip, self.received_port))
        gw.pipe_in.put(pf.port_pong % self.local_port)
        gw.pipe_in.put(None)
        gw.run()

    # //011// {"i": 'h3xd1'} ///  ->  //100// {"h": '1111', "t": '0102', "L": 0|1} ///
    def login_pong(self, *_, **__):
        if self.received_port:
            hand, dep_time, lapsed = self.login(self.header)
            if hand:
                gw = GateWayQS((self.client_ip, self.received_port))
                gw.pipe_in.put(pf.login_pong % (hand, dep_time, lapsed))
                gw.pipe_in.put(None)
                gw.run()
            del hand, dep_time, lapsed
        if not self.client_is_verified(): raise ConnectionResetError

    # //100// {"h": '1111', "t": '0102', "L": 0|1} ///  ->  None
    def login_handshake(self, *_, **__) -> None:
        self.login_shake(self.header)
        if not self.client_is_verified(): raise ConnectionResetError

    # //101// {"i": 'h3xd1', "I": 'h3xd1'} ///
    # ->  //020// //110// {"T": "P", "l": <length>} /// ///
    #     data
    # ->  //020// //110// {"T": "H", "l": <length>} /// ///
    #     data
    def login_change(self, *_, **__):
        try:
            hand, dep_time, refreshed_config = self.login(self.header, change=self.client_cache[self.client_ip][2])
            if hand:
                configs = self.read_hostfsc()
                self.pipe_out.put(pf.bend % pf.w_conf % (b'P', len(configs[0])))
                self.pipe_out.put(configs[0])
                self.pipe_out.put(pf.bend % pf.w_conf % (b'H', len(configs[1])))
                self.pipe_out.put(configs[1])
            del hand, dep_time, refreshed_config
            self.header = None
        finally:
            self.header = None

    # //111// {"T":"[b|B][c|C][f|F][g]"} ///  ->  //002|020// //RES// 200 /// ///
    def reset_(self, *_, **__):
        targets = self.header.option_liev.get('T')
        if 'B' in targets: self.pipe_out.put(pf.bend % resp.formNDF % str(self.wrapper_ips__(
            clear_cache=True)).encode(CNF.SRM_ENC))
        elif 'b' in targets: self.pipe_out.put(pf.bend % resp.formNDF % str(self.wrapper_ips__(
            )).encode(CNF.SRM_ENC))
        if 'C' in targets: self.pipe_out.put(pf.bend % resp.formNDF % str(self.wrapper_call__(
            clear_cache=True)).encode(CNF.SRM_ENC))
        elif 'c' in targets: self.pipe_out.put(pf.bend % resp.formNDF % str(self.wrapper_call__(
            )).encode(CNF.SRM_ENC))
        if 'F' in targets:
            self.pipe_out.put(pf.close_gateway % resp.rRES(resp.CODEs.OK))
            sleep(.2)
            self.fw_full_reset()
            raise ConnectionResetError
        elif 'f' in targets:
            self.pipe_out.put(pf.bend % resp.rRES(resp.CODEs.OK))
            self.fw_reset()
        if 'g' in targets:
            self.pipe_out.put(pf.close_gateway % resp.rRES(resp.CODEs.OK))
            raise ConnectionResetError

    # //000//  ///  ->  //002// //RES// 200 /// ///
    def ls_shutdown(self, *_, **__):
        self.pipe_out.put(pf.close_gateway % resp.rRES(resp.CODEs.OK))
        self.keep_alive = False
        raise ConnectionResetError

    # //110// {"l":<n>} ///
    def __bend(self, *_, **__):
        length = self.header.option_liev.get("l")
        if length > 15000:
            self.pipe_out.put(resp.iERR(resp.CODEs.LengthRequired))
            return
        self.pipe_out.put(self.header)
        for _ in CNF.BUFFER_ITER(length):
            data = self.sock.recv(CNF.DAT_SOCK_BUFFER)
            if not data:
                self.pipe_out.put(resp.iERR(resp.CODEs.ExpectationFailed))
                return
            self.pipe_out.put(data)

    # //200//  ///
    def _stone(self, *_, **__):
        pass

    # //022//  ///
    def t_kill(self, *_, **__):
        try:
            for _attr in CNF.__dir__():
                if _attr.startswith("_"): continue
                if _attr in CNF._NOTPICKLE: continue
                setattr(CNF._CNF_PROX, _attr, getattr(CNF, _attr))
            if self.client_is_verified(): self.client_cache.pop(self.client_ip)
            LOGS_.kill.logg(35, CNF.STRINGS.KILL_THREAD, ico=CNF.PRINT_ICOS.kill, ip=self.client_ip, cache=self.client_cache)
            LOGS_.kill.logg(20 - CNF.SIDE_[True] * 10, CNF.STRINGS.KILL_LOG % (str(self.client_cache), str(self.lapsdelset), str(argv)), ip=self.client_ip, cache=self.client_cache)
            LOGS_.kill.logg(35, CNF.STRINGS.KILL_BACKUP, ico=CNF.PRINT_ICOS.recycle, ip=self.client_ip, cache=self.client_cache)
            for SIG in CNF.SIG_SEQ:
                kill(getpid(), SIG)
        except Exception as e:
            CNF.EXP_EXIT(e)

    def run(self) -> None:

        with socket(AF_INET, SOCK_STREAM) as _SOCK:

            _SOCK.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            for p in range(self.port_range[0], self.port_range[1] + 1):
                try:
                    _SOCK.bind((self.local_address, p))
                except OSError as err:
                    if err.errno == 98: pass
                    else: raise err
                else:
                    self.local_port = p
                    break
            if not self.local_port:
                LOGS_.blackbox.logg(60, CNF.STRINGS.PORT_INIT % str(self.port_range), ico=CNF.PRINT_ICOS.err)
                CNF.EXP_EXIT(0)
            LOGS_.blackbox.logg(25, CNF.STRINGS.LISTENER % (self.local_address, self.local_port), ico=CNF.PRINT_ICOS.listen)

            _SOCK.listen(1)
            with CNF._SSL_CONT_RECEIVER.wrap_socket(_SOCK, server_side=True) as SOCK_:

                while self.keep_alive:

                    self.client_set.clear()
                    self.client_ip = str()
                    LOGS_.sockio.logg(20, CNF.STRINGS.NEW_SESSION % self.client_cache, ico=CNF.PRINT_ICOS.listen)

                    rec_sock, addr = SOCK_.accept()

                    self.client_set.add(addr)
                    self.client_ip = addr[0]
                    LOGS_.sockio.logg(25, CNF.STRINGS.REC_CONNECTION % self.client_set, ico=CNF.PRINT_ICOS.i_pipe)

                    try:
                        if not self.ip_on_board(rec_sock): continue
                    except OverflowError: break

                    try:
                        if not self.client_is_verified():
                            self.client_cache[self.client_ip][0] += 1
                            self.client_is_verified()
                    except PermissionError:
                        self.client_cache[self.client_ip][0] += 1
                        continue
                    except OverflowError: break

                    LOGS_.sockio.logg(10, CNF.STRINGS.FW_PASSED, ico=CNF.PRINT_ICOS.sharp)

                    client_is_ = True
                    while self.keep_alive and client_is_:
                        client_is_ = self.client_is_verified()

                        try:

                            self.header = self.StreamHeader(rec_sock)
                            port_method = self.intercept_methods.get(self.header.method)
                            if port_method:
                                self.sock = rec_sock
                                try:
                                    self._client_cache = self.client_cache
                                    self.call(self.header, port_method, header=self.header)
                                except PermissionError:
                                    if self.client_is_verified():
                                        self.pipe_out.put(resp.iERR(resp.CODEs.Unauthorized))
                                    if self.header.option_json:
                                        if _l := self.header.option_json.get('l'):
                                            for _ in CNF.BUFFER_ITER(_l): self.sock.recv(CNF.DAT_SOCK_BUFFER)
                                        for stack in range(1, CNF.DAT_MAX_STACKS + 1):
                                            if _l := self.header.option_json.get('l%d' % stack):
                                                for _ in CNF.BUFFER_ITER(_l): self.sock.recv(CNF.DAT_SOCK_BUFFER)
                                            else: break
                                self.sock = None
                                continue

                            if not client_is_: continue

                            if not self.header.header:
                                continue

                            if not self.header.option_liev:
                                self.pipe_out.put(resp.iINF(resp.CODEs.SwitchingProto))

                            self.pipe_out.put(self.header)

                            for stack in range(1, CNF.DAT_MAX_STACKS + 1):
                                try:
                                    if _l := self.header.option_json.get('l%d' % stack):
                                        for _ in CNF.BUFFER_ITER(_l):
                                            data = rec_sock.recv(CNF.DAT_SOCK_BUFFER)
                                            if not data: raise BufferError
                                            self.pipe_out.put(data)
                                    else: break
                                except AttributeError:
                                    break
                                except BufferError:
                                    self.pipe_out.put(resp.iERR(resp.CODEs.ExpectationFailed))
                                except (ValueError, TypeError):
                                    self.pipe_out.put(resp.iERR(resp.CODEs.LengthRequired))

                        except ConnectionResetError as e:
                            LOGS_.sockio.logg(10, type(e), e, ip=self.client_ip, cache=self.client_cache, mt=self.run)
                            if self.client_is_verified(tox_sock=rec_sock):
                                self.client_cache.pop(self.client_ip)
                                self.pipe_out.put(pf.close_gateway % b'')
                                sleep(.5)
                            while not self.pipe_out.empty(): self.pipe_out.get()
                            break

                        except Exception as e:
                            LOGS_.blackbox.logg(60, type(e), e, *exp_full_trace(e), ip=self.client_ip, cache=self.client_cache, mt=self.run, ansi=CNF.MSG_ANSI.red)
                            if self.client_is_verified(tox_sock=rec_sock):
                                self.client_cache.pop(self.client_ip)
                                self.pipe_out.put(pf.close_gateway % b'')
                                sleep(.5)
                            while not self.pipe_out.empty(): self.pipe_out.get()
                            break

                        finally:
                            if not self.client_is_verified():
                                rec_sock.close()

                LOGS_.blackbox.logg(25, CNF.STRINGS.LISTENER_CLOSE, ico=CNF.PRINT_ICOS.close)
