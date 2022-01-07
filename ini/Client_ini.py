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

from time import sleep, time
from os import get_terminal_size
from sys import stdout

from _rc._run import configurations
from _rc._OBJrc import configurations as CNF

from sec.Loggers import LOGS_
from prc.Gateways import GateWayQQ, GateWayQS
from prc.SocketPort import SockPort
from sec.Proto import pf
from prc.Bridge import BridgeFactory, PortFactory
from sec.fscIO import pph
from sec.fTools import ConsoleParser, print_manualpage, exp_full_trace

DEBUG = False
hasattr(configurations, "__file__")
_RECEIVER_IP = None

class Connect:
    def __init__(self):
        global _RECEIVER_IP

        self.l_sock = SockPort(CNF.PORT_RANGE_ESTABLISH, CNF.IP_LOCAL)
        self.l_sock.setDaemon(True)
        self.l_sock.start()
        while not self.l_sock.local_port: sleep(0.1)

        for _RECEIVER_IP in CNF.IP_RECEIVER:
            LOGS_.blackbox.logg(25, CNF.STRINGS.SEND_PINGS_TO % _RECEIVER_IP, ico=CNF.PRINT_ICOS.pings)
            try:
                for p in range(CNF.PORT_RANGE_RECEIVER[0], CNF.PORT_RANGE_RECEIVER[1] + 1):
                    if self.l_sock.received_port: break
                    try:
                        gw = GateWayQS((_RECEIVER_IP, p), _quiet=True)
                        gw.pipe_in.put(pf.port_ping % self.l_sock.local_port)
                        gw.pipe_in.put(None)
                        gw.run()
                    except ConnectionRefusedError:
                        pass
                if not self.l_sock.received_port:
                    LOGS_.blackbox.logg(25, CNF.STRINGS.PINGS_SEND, ico=CNF.PRINT_ICOS.pings)
                    for i in range(20):
                        if self.l_sock.received_port: break
                        if not self.l_sock.client_ip: print(CNF.PRINT_TIMEOUT_BAR[i], flush=True, end='')
                        sleep(CNF.PING_TIMEOUT)
                    if not self.l_sock.received_port:
                        LOGS_.blackbox.logg(40, CNF.STRINGS.NO_REC_PORT % str(CNF.PORT_RANGE_RECEIVER), ico=CNF.PRINT_ICOS.x)
            except KeyboardInterrupt: pass
        if not self.l_sock.received_port:
            LOGS_.blackbox.logg(60, CNF.STRINGS.NO_REC_PORT_FIN % str(CNF.IP_RECEIVER), ico=CNF.PRINT_ICOS.x, ansi=CNF.MSG_ANSI.red)
            CNF.EXP_EXIT(1)
        try:
            login = pph()
        except KeyboardInterrupt:
            exit(0)
        if CNF.DO_PAR:
            LOGS_.blackbox.logg(35, CNF.STRINGS.PAR_REQ % _RECEIVER_IP, ico=CNF.PRINT_ICOS.bind, ansi=CNF.MSG_ANSI.bold)
            self.l_sock._pair_pair = (_RECEIVER_IP, time())
            self.l_sock._pair_parts = {'P': CNF.FSC_ESTABLISH_PEPPER % CNF.USER, 'H': CNF.FSC_ESTABLISH_TABLE_FILE % CNF.USER}
            gw = GateWayQS((_RECEIVER_IP, self.l_sock.received_port))
            gw.pipe_in.put(pf.do_pair % (CNF.USER.encode(CNF.SRM_ENC), login.encode(CNF.SRM_ENC)))
            gw.pipe_in.put(None)
            gw.run()

        self.l_sock.local_login = login

        # run once for enrolment
        gw = GateWayQS((_RECEIVER_IP, self.l_sock.received_port))
        gw.pipe_in.put(pf.login_ping % (CNF.USER.encode(CNF.SRM_ENC), login.encode(CNF.SRM_ENC)))
        gw.pipe_in.put(None)
        gw.run()

        # establish sender - receiver daemon
        self.gateway_qs = GateWayQS((_RECEIVER_IP, self.l_sock.received_port))
        self.gateway_qs.setDaemon(True)
        self.gateway_qs.start()

        LOGS_.blackbox.logg(25, CNF.STRINGS.HANDSHAKE_TIMEOUT, ico=CNF.PRINT_ICOS.pings)
        for i in range(20):
            sleep(CNF.PING_TIMEOUT)
            print(CNF.PRINT_TIMEOUT_BAR[i], flush=True, end='')
            if self.l_sock.client_is_verified():
                self.gateway_qq = GateWayQQ(self.l_sock.pipe_out,
                                            self.gateway_qs.pipe_in,
                                            {self.l_sock.client_ip: self.l_sock.client_cache[self.l_sock.client_ip]})
                self.gateway_qq.setDaemon(True)
                self.gateway_qq.start()
                break

        if not self.l_sock.client_is_verified():
            LOGS_.blackbox.logg(60, CNF.STRINGS.NO_REC_HANDSHAKE, ico=CNF.PRINT_ICOS.x, ansi=CNF.MSG_ANSI.red)
            CNF.EXP_EXIT(1)

        self.PIPE = self.gateway_qs.pipe_in
        LOGS_.blackbox.logg(25, CNF.STRINGS.PIPE_PROVIDED, ico=CNF.PRINT_ICOS.bridge_on)
        self.BRIDGE = self.gateway_qq
        LOGS_.blackbox.logg(25, CNF.STRINGS.BRIDGE_PROVIDED, ico=CNF.PRINT_ICOS.bridge_on)
        if CNF.INSPECT_BINDING:
            LOGS_._setSockstream()
            LOGS_.blackbox.logg(25, CNF.STRINGS.INSPECTTRM_AT % CNF.INSPECT_BINDING, ico=CNF.PRINT_ICOS.lswush)


class Console(Connect, PortFactory, BridgeFactory, ConsoleParser):

    def __init__(self):
        Connect.__init__(self)
        BridgeFactory.__init__(self, self.PIPE, self.BRIDGE)
        ConsoleParser.__init__(self, {}, {})
        PortFactory.__init__(self, self.PIPE, self.BRIDGE)

        self.intercept_options = {'--help': (print_manualpage, 'parser')}

        self.CMD_CONFIG = {
            'get': (self.mks_GET, {
                (1, 3): {'n?[lL]': (-1,), 'n?[fFaA]': (1, -1), 'n?(r{1,2}|R{1,2})': (1, -1), '--help': 0, '--List': 0,
                         '--list': 0, '--tform': 2, '--tutc': -2, '--write': -2, '--enum': 0}, None: '-f'}),
            'put': (self.mks_PUT, {(1, 3): {'n?[fFaA]': (1, -1), 'n?(r{1,2}|R{1,2})': (1, -1), '--help': 0}, None: '-f'}),
            'log': (self.send_LOG, {1: {'[jt]': 2, '--help': 0}, None: '-t'}),
            'cd': (self.mks_CHD, {1: {'[SDsdAa]': 1, '--help': 0}, None: '-a'}),
            'pwd': (self.mks_PWD, {(1, 3): {'[pcuaL]{1,3}': 0, '--help': 0, '--list': 0}, None: '-p'}),
            'ch': (self.send_change_login, {1: {'--login': 0, '--help': 0}}),
            'reset': (self.send_reset, {(1, 4): {'[bBcCfFg]{1,4}': 0, '--help': 0}}),
            'shutdown': (self.send_shutdown, {1: {None: 0, '--help': 0}}),
            'kill': (self.send_kill, {1: {None: 0, '--help': 0}}),
            '_err': (self.send_err, {1: {None: -2, '--help': 0}}),
            'echo': (self.send_err, {1: {None: -2, '--help': 0}}),
            '_pipe': (self.mnlpipei, {1: {None: -2, '--help': 0}}),
            'clear': (self.clear_lns, {1: {None: 0, '--help': 0}}),
            'help': (print_manualpage, {1: {'--help': 0}, None: '--help'}),
            'logging': (LOGS_.CNSentry, {
                1: {None: 0, '--sockclose': 0, '--sock': -2, '--io': 0, '--debug': 0, '--reset': 0, '--blackbox': 0,
                    '--allS': 2, '--allF': 2, '--help': 0}}),
            'exec': (self.EXEC, {1: {None: 2, '--help': 0}}),
            'bypass': (self.bypass, {1: {None: 0, '--help': 0}}),
            'exit': (exit, {1: {None: -2}}),
            '0': (exit, {1: {None: -2}}),
        }

    @staticmethod
    def clear_lns():
        n_lns = get_terminal_size()[1]
        CNF.PCONT += '\n' * (n_lns + 1)
        if CNF.SYS_PLATFORM == "w": CNF.PCONT += "!INFO: your console may does not support ANSI-Codes\n"
        CNF.PCONT += '\x1b[%dA' % n_lns

    @staticmethod
    def bypass():
        if CNF._BYPASS and CNF._BYPASSED.name == "<ByPass>":
            print("\n", file=CNF._BYPASSED)
            CNF._BYPASSED = stdout
        elif CNF._BYPASS:
            CNF._BYPASSED = CNF._BYPASS
        else:
            CNF.PCONT += "]] NotConfigured [[\n"

    @staticmethod
    def EXEC(__s: str):
        try:
            exec(__s)
        except Exception as e:
            print(f"[ERR] {type(e)} {e}")

    def mnlpipei(self, dat: str=None):
        if dat: return self.PIPE.put(dat.encode(CNF.SRM_ENC))
        if CNF._BYPASSED.name == "<ByPass>": return
        while True:
            try:
                dat = input("]<<- ").encode(CNF.SRM_ENC)
                if dat in (b'exit', b'done', b'0', b'quit', b'x', b'X'): break
                self.PIPE.put(dat)
            except (KeyboardInterrupt, EOFError): break

    def main(self):
        while True:
            try:
                if CNF._BYPASSED.name == "<ByPass>":
                    inp = CNF._BYPASS.read()
                else:
                    inp = input(f"{(_rcode[0] if (_header := self.BRIDGE.header) and (_rcode := _header.option_list) else '')}] : ")
                if inp.strip() in ('exit', 'done', '0', 'quit', 'x', 'X'): raise EOFError(inp)

                if opts := self.pars_string(inp):
                    if None in opts[0]:
                        self.func.__call__(*opts[0][None])
                    elif opts_args := self.get_merged():
                        self.func.__call__(opts_args[0], *opts_args[1])

                if CNF._BYPASSED.name == "<ByPass>":
                    rcode = f"[{(_rcode[0] if (_header := self.BRIDGE.header) and (_rcode := _header.option_list) else '')}]"
                    if len(CNF.PCONT) > 1:
                        print(CNF.PCONT[1:] + rcode, file=CNF._BYPASSED)
                    else:
                        print(CNF.PCONT + rcode, file=CNF._BYPASSED)
                    CNF.PCONT = '\n'
                    print(rcode, flush=True, end="")
                elif len(CNF.PCONT) > 1:
                    print(CNF.PCONT[1:], flush=True)
                    CNF.PCONT = '\n'

            except EOFError as e:
                LOGS_._closeSockstream()
                print(f"{e}\n[[ 0 ]]\n", file=CNF._BYPASSED)
                exit()
                break

            except KeyboardInterrupt:
                print()

            except Exception as e:
                trace = ""
                if DEBUG:
                    trace = exp_full_trace(e)
                print(f"{type(e)} {e} {trace}")
                sleep(.5)


def main():
    Console().main()
