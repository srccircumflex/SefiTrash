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

from _rc._OBJrc import configurations as CNF

from sec.Loggers import LOGS_
from sec.Bypass import InterventionEXEC
from sec.fTools import exp_full_trace
from prc.SocketPort import SockPort, pf
from prc.Gateways import GateWayQQ, GateWayQS


class Init(InterventionEXEC):

    def __init__(self, _kill_backup):
        InterventionEXEC.__init__(self)

        self.l_sock = SockPort(CNF.PORT_RANGE_RECEIVER, CNF.IP_LOCAL)
        self.l_sock.setDaemon(True)
        self.l_sock.client_cache = _kill_backup

        if CNF.PROVIDED_PARING:
            LOGS_.blackbox.logg(35, CNF.STRINGS.PROVIDE_PAR % CNF.PROVIDED_PARING, mt=self.__init__, ico=CNF.PRINT_ICOS.key, ansi=CNF.MSG_ANSI.bold)
            self.l_sock._pair_parts = {
                'H': CNF.AUTH_CONF[CNF.PROVIDED_PARING[0]]['hst'],
                'P': CNF.AUTH_CONF[CNF.PROVIDED_PARING.pop(0)]['ppp']}
            self.l_sock._pair_pair = CNF.PROVIDED_PARING.pop(0)
        self.l_sock.start()

        if CNF.MOD_BGSTREAM and CNF.INSPECT_BINDING:
            LOGS_.blackbox.logg(25, CNF.STRINGS.INSPECTTRM_AT % CNF.INSPECT_BINDING, ico=CNF.PRINT_ICOS.lswush)
            LOGS_._setSockstream()

        try:
            while self.l_sock.is_alive():

                while self.l_sock.is_alive():

                    self.jread()

                    if self.l_sock.client_cache.get(self.l_sock.client_ip):
                        sleep(CNF.KILL_TIMEOUT)
                        try:
                            if self.l_sock.client_cache.get(self.l_sock.client_ip)[1]:
                                break
                            else:
                                self.l_sock.t_kill()
                        except (TypeError, KeyError) as e:
                            LOGS_.blackbox.logg(0, f"{type(e)} {e} {exp_full_trace(e)}")

                    sleep(CNF.LISTEN_TIMEOUT)

                if not self.l_sock.is_alive(): break

                self.gateway_qs = GateWayQS(
                    (self.l_sock.client_ip, self.l_sock.client_cache.get(self.l_sock.client_ip)[1]))
                self.gateway_qq = GateWayQQ(
                    self.l_sock.pipe_out,
                    self.gateway_qs.pipe_in,
                    {self.l_sock.client_ip: self.l_sock.client_cache[self.l_sock.client_ip]})
                self.gateway_qs.setDaemon(True)
                self.gateway_qs.start()
                self.gateway_qq.setDaemon(True)
                self.gateway_qq.start()

                while True:
                    if not self.gateway_qq.is_alive() and not self.gateway_qs.is_alive(): break
                    if self.gateway_qs.pipe_in.empty() and not GateWayQQ.pipe_lock:
                        self.gateway_qs.pipe_in.put(pf.pick)
                        self.jread()
                    sleep(5)

                LOGS_.blackbox.logg(35, CNF.STRINGS.CLOSE_GW_FLAG, ico=CNF.PRINT_ICOS.off)

            exit(0)

        except KeyboardInterrupt: exit('')
