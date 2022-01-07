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


from ast import literal_eval
from re import search, sub
from functools import lru_cache

from _rc import configurations as CNF
from sec.Loggers import LOGS_

# Permission-Levels {
#                       i: login required
#                       4: host -> client interaction
#                       3: admin
#                       2: std+
#                       1: std
#                       0: non-relevant,
#                      -1: non-relevant(handled by other Control),
#                      -2: non-relevant(used local, intern)
#                   }
#                                      client -> host effect  [host-side]                        [client-side]
class PortMethods:
    def __init__(self):
        self._shutdown =             b'000'  # i 3         # program exit          ->              response OK
        self._port_ping =            b'001'  # -1          # save client port      ->              host port
        self._port_pong =            b'010'  # -1, 4       !# save client port
        self._login_ping =           b'011'  # -1          # login                 ->              handshake
        self._login_pong =           b'100'  # -1, 4       !# ERROR (handled)
        self._do_login_change =      b'101'  # i 1         # change perm-files     ->              perm-files
        self._w_conf =               b'110'  # i 4         !# ERROR (NOT HANDLED)
        self._do_reset =             b'111'  # i 3         # reset (below)*        ->              response
        self._close_gateway =        b'002'  # i 1         # close bridge- and send- gateway
        self._bend =                 b'020'  # i 0, -2     !# echo rare header.option   ->
        self._kill =                 b'022'  # i 2         # save, kill, restart
        self._pick =                 b'200'  # 0, 4        !# nothing
        self._pair =                 b'202'  # -1          # pair if provided
        self._ierr =                 b'220'  # i 0, -2     !# echo header.option as error-response   ->

pm = PortMethods()

class PortFormats(PortMethods):
    def __init__(self):
        PortMethods.__init__(self)
        self.port_ping =     b'//%b// %b ///' % (self._port_ping, b'%d')
        self.port_pong =     b'//%b// %b ///' % (self._port_pong, b'%d')
        self.login_ping =    b'//%b// {"u":"%b","i":"%b"} ///' % (self._login_ping, b'%b', b'%b')
        self.login_pong = b'//%b// {"h":"%b","t":"%b","L":%b} ///' % (self._login_pong, b'%b', b'%b', b'%d')
        self.close_gateway = b'//%b// %b ///' % (self._close_gateway, b'%b')
        self.w_conf = b'//%b// {"T":"%b","l":%b} ///' % (self._w_conf, b'%b', b'%d')
        self.bend = b'//%b// %b ///' % (self._bend, b'%b')
        self.pick = b'//%b//  ///' % self._pick
        self.reset = b'//%b// {"T":"%b"} ///' % (self._do_reset, b'%b')                     # * "T":"[b|B][c|C][f|F][g]"
        self.pair = b'//%b// {"T":"%b","l":%b} ///' % (self._pair, b'%b', b'%d')
        self.do_pair = self.pair % (b'""//x// {"u":"%b","i":"%b"} ///""', 0)
        self.ierr = b'//%b// %b ///' % (self._ierr, b'%b')
        self.do_login_change = b'//%b// {"i":"%b","I":"%b"} ///' % (self._do_login_change, b'%b', b'%b')
        self.shutdown = b'//%b//  ///' % self._shutdown
        self.kill = b'//%b//  ///' % self._kill

# *

# b     return board-wrapper-info as RES        # B     + clear cache
# c     return secure-call-wrapper-info as RES  # C     + clear cache
# g     close gateways
# f     fw_reset                                # F     fw_full_reset, close GWS, ConnectionReset
#  - clear cache from unverified clients        #  + clear all caches and received id's
#  - reset counters / board wrapper cache       #  + reset firewall interval

pf = PortFormats()


class ModuleMethods:
    def __init__(self):
        self.GET = b'GET'
        self.PUT = b'PUT'
        self.LOG = b'LOG'
        self.CHD = b'CHD'
        self.RET = b'RET'
        self.PWD = b'PWD'

mm = ModuleMethods()


class ModuleFormats(ModuleMethods):
    def __init__(self):
        ModuleMethods.__init__(self)
        self.PWD_f   = b'//%b// %b ///' % (self.PWD, b'{"m":"%b"}')
        self.RET_f   = b'//%b// %b ///' % (self.RET, b'{"m":"%b","l1":%d}')
        self.CHD_f   = b'//%b// %b ///' % (self.CHD, b'{"m":"%b","l1":%d}')
        self.GET_f  = b'//%b// %b ///' % (self.GET, b'{"m":"%b","l1":%d}')
        self.GET_sub = b'{"S":"%b","D":"%b"}'
        self.PUT_f  = b'//%b// %b ///' % (self.PUT, b'{"m":"%b","l1":%d,"l2":%d}')
        self.LOG_f   = b'//%b// %b ///' % (self.LOG, b'{"m":"%b", "l1":%d}')


class RCodes:

    class CODEs:

        Continue = b'100'
        SwitchingProto = b'101'
        Processing = b'102'
        OK = b'200'
        Created = b'201'
        Accepted = b'202'
        BadRequest = b'400'
        Unauthorized = b'401'
        Forbidden = b'403'
        NotFound = b'404'
        NotAcceptable = b'406'
        Conflict = b'409'
        LengthRequired = b'411'
        PayloadTooLong = b'413'
        ExpectationFailed = b'417'
        Locked = b'423'
        HeaderTooLarge = b'431'
        InternalError = b'500'
        NotImplementError = b'501'
        ServiceUnavailable = b'503'
        StorageInsufficient = b'507'

    def __init__(self):

        self.CODE_TO_NAME = {c: n for c, n in zip(
            self.CODEs.__dict__.values(),
            self.CODEs.__dict__.keys()
        ) if not n.startswith('_')}

        self.formEXPi = pf.ierr % b'>%b< / %b'
        self.formERRi = pf.ierr % b'>%b<'
        self.formINFi = pf.ierr % b'-%b-'
        self.formEXPb = b'        {%b} / %b'
        self._RES = b'//RES// %b ///'
        self.formNDF = self._RES % b'#%b#'
        self.formRES = self._RES % b'[%b]'

    def iEXP(self, cod:bytes, exp:bytes) -> bytes: return self.formEXPi % (cod, (exp if type(exp) == bytes else str(exp).encode(CNF.SRM_ENC)))
    def iERR(self, cod:bytes) -> bytes: return self.formERRi % cod
    def iINF(self, cod:bytes) -> bytes: return self.formINFi % cod
    def bEXP(self, cod:bytes, exp:bytes) -> bytes: return self.formEXPb % (cod, (exp if type(exp) == bytes else str(exp).encode(CNF.SRM_ENC)))
    def rRES(self, cod:bytes) -> bytes: return self.formRES % cod
    def rNDF(self, dat:bytes) -> bytes: return self.formNDF % (dat if type(dat) == bytes else str(dat).encode(CNF.SRM_ENC))

    def get_response(self, data:bytes):
        if data[8] == 62:  # '>' -- internal Error and Exception
            LOGS_.bridge.logg(45, data, mt=self.get_response, ico=CNF.PRINT_ICOS.exclam2)
            return self.rRES(data[9:12])
        elif data[8] == 123:  # '{' -- module Exception
            LOGS_.bridge.logg(40, data, mt=self.get_response, ico=CNF.PRINT_ICOS.exclam)
            return self.rRES(data[9:12])
        elif data[8] == 45:  # '-' -- internal Info
            LOGS_.bridge.logg(30, data, mt=self.get_response, ico=CNF.PRINT_ICOS.exclam)
            return self.rRES(data[9:12])
        elif data[8] == 91:  # '[' -- ord response
            return data
        else:
            LOGS_.blackbox.logg(50, data, mt=self.get_response, ico=CNF.PRINT_ICOS.exclam2)
            LOGS_.bridge.logg(50, data, mt=self.get_response, ico=CNF.PRINT_ICOS.exclam)
            return self.rNDF(option_pattern(data))

resp = RCodes()


def header_pattern(header:bytes) -> object: return search(b'^//\w+// .* ///$', header)
def method_pattern(header:bytes) -> bytes: return search(b'\w+', search(b'^//\w+// ', header).group()).group()
def option_pattern(header:bytes) -> bytes: return sub(b' ///$', b'', sub(b'^//\w+// ', b'', header))
def hexdig_pattern(option:bytes) -> str: return search(b'^[a-z0-9]+$', option).group().decode(CNF.SRM_ENC)

class ParseStreamHeader:

    @lru_cache(3)
    def __init__(self, header:bytes):

        self.header: bytes = header
        self.method: bytes = None
        self.option: bytes = None
        self.option_liev = None
        self.option_json: dict = None
        self.option_int: int = None
        self.option_list: list = None
        self.option_hexd: str = None

        try:
            if not header_pattern(self.header):
                self.header = resp.iEXP(resp.CODEs.Unauthorized, self.header)
            self.method = method_pattern(self.header)
            self.option = option_pattern(self.header)
        except (TypeError, AttributeError):
            pass

        if self.option:

            try:
                self.option_hexd = hexdig_pattern(self.option)
            except AttributeError:
                pass
            try:
                self.option_liev = literal_eval(self.option.decode(CNF.SRM_ENC))
                if type(self.option_liev) == dict: self.option_json = self.option_liev
                elif type(self.option_liev) == list: self.option_list = self.option_liev
                elif type(self.option_liev) == int: self.option_int = self.option_liev
            except (SyntaxError, ValueError):
                pass


class StreamHeader:

    def __init__(self, sock):

        self.header: bytes = sock.recv(64)
        self.method: bytes = b''
        self.option: bytes = b''
        self.option_liev = None
        self.option_json: dict = None
        self.option_int: int = None
        self.option_list: list = None
        self.option_hexd: str = None

        if not self.header: return

        try:
            c = 1
            while not self.header.endswith(b' ///'):
                c += 1
                if c > CNF.DAT_MAXSIZE_HEADER:
                    raise OverflowError('StreamHeader > max')
                data = sock.recv(64)
                if not data: raise OverflowError('StreamHeader > max')
                self.header += data
        except OverflowError:
            self.header = resp.iEXP(resp.CODEs.HeaderTooLarge, self.header)

        LOGS_.sockio.logg(15, self.header, mt=self.__init__)

        if not header_pattern(self.header):
            self.header = resp.iEXP(resp.CODEs.Unauthorized, self.header)

        try:
            self.method = method_pattern(self.header)
            self.option = option_pattern(self.header)
        except (TypeError, AttributeError):
            self.header = resp.iEXP(resp.CODEs.BadRequest, self.header)

        if self.option:
            try:
                self.option_hexd = hexdig_pattern(self.option)
            except AttributeError:
                pass
            try:
                self.option_liev = literal_eval(self.option.decode(CNF.SRM_ENC))
                if type(self.option_liev) == dict: self.option_json = self.option_liev
                elif type(self.option_liev) == list: self.option_list = self.option_liev
                elif type(self.option_liev) == int: self.option_int = self.option_liev
            except (SyntaxError, ValueError):
                pass
            except Exception as e:
                LOGS_.blackbox.logg(60, type(e), e, mt=self.__init__)
                self.header = resp.iEXP(resp.CODEs.InternalError, f"!{e} /".encode(CNF.LOC_ENC) + self.header)
