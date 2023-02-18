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
from calendar import timegm
from os import access, makedirs
from os import path as os_path
from re import escape, findall, search, sub
from time import gmtime, strftime, strptime, time
from functools import lru_cache

from _rc import configurations as CNF

from sec.fTools import DefIfEndIf, subwinpath, subwininval
from sec.Proto import StreamHeader, ParseStreamHeader, pm
from sec.Loggers import LOGS_, log_bad_data
from sec.vTools import mk_login, _rcUDELUser, _rcDELUser
from sec.fscModule import FStreamCipher


def ip_rex(ip:str) -> str: return '^' + sub(
    '(\.0$|\\\.0$)', '\\.[0-9]+', sub(
        '(\.0\.|\\\.0\.)','\\.[0-9]+\\.', sub(
            '(\.0\.|\\\.0\.)','\\.[0-9]+\\.',sub(
                '^0\.', '[0-9]+\\.', ip)))) + '$'


class SecureCall:

    call_cache: dict = dict()

    def __init__(self, client_set):

        self.NONE_ACCEPTS: set = {
            pm._port_ping, pm._port_pong,
            pm._login_ping, pm._login_pong,
            pm._pair
        }

        self.HOST_DROP: set = {
            pm._port_pong,
            pm._login_pong,
            pm._w_conf,
        }

        self.CLIENT_DROP: set = {
            pm._port_ping,
            pm._login_ping
        }

        self._MAP = {CNF.CLIENT_SIDE: self.CLIENT_DROP, CNF.HOST_SIDE: self.HOST_DROP}

        self._defifendifSC = DefIfEndIf(CNF.BOARD_CALL_RULE, *CNF.IFDEFENDIF['BOARD_CALL_RULE'])
        self._delim = b'\\\\'

        self._client_cache:dict = None
        self._client_set:set = client_set

        self._none_accept = b'(' + bytes().join(
            [b'^' + n + b'$|' for n in self.NONE_ACCEPTS]
        )[:-1] + b')'

        self.drop = b'(' + bytes().join(
            [b'^' + n + b'$|' for n in self._MAP[True]]
        )[:-1] + b')'

    __ol = None

    @lru_cache(20)
    def _read_rule(self, user:str, __m:bytes, __el:bytes) -> bool:

        if CNF.CLIENT_SIDE: return True
        if not self._defifendifSC.configured:
            if user:
                LOGS_.blackbox.logg(30, CNF.STRINGS.ENDIF % 'BOARD_CALL_RULE', ip=user, ico=CNF.PRINT_ICOS.rc, ansi=CNF.MSG_ANSI.yellow, mt=self._read_rule)
            return True
        _rrc = self._defifendifSC.read_rc()
        _configured = False
        try:
            while True:
                ln = next(_rrc)
                delim_splt = (ln.strip() + b' ').split(self._delim)
                if len(delim_splt) < 2: continue
                if ln.split()[0] != user.encode(CNF.LOC_ENC): continue
                _configured = True
                for ip in delim_splt[0].decode(CNF.LOC_ENC).split()[1:]:
                    if search(ip_rex(ip), self._client_set.copy().pop()[0]):
                        if search(b' ' + __m + b' ', delim_splt[1]): raise PermissionError

                        if not self.call_cache.get(user):
                            limitations = findall(__m + b'\[[0-9]+]', delim_splt[1])
                            for limited in limitations:
                                self.call_cache.setdefault(user, dict())
                                self.call_cache[user].setdefault(
                                    __m.decode(CNF.LOC_ENC), [int(sub(__m + b'\[|]', b'', limited)),0])

                        distinct = findall(__m + b'\([^(]*\)', delim_splt[1])
                        for dist in distinct:
                            args = sub(__m + b'\(|\)| ', b'', dist).split(b';')
                            for arg in args:
                                _key, _val = arg.split(b':')
                                key, val = _key.decode(CNF.LOC_ENC), _val.decode(CNF.LOC_ENC)
                                if key in self.__ol:
                                    if val.startswith('<'):
                                        val = int(val.replace('<', '').replace('.', ''))
                                        if self.__ol[key] < val: raise PermissionError
                                    elif val.startswith('>'):
                                        val = int(val.replace('>', '').replace('.', ''))
                                        if self.__ol[key] > val: raise PermissionError
                                    elif search("[" + val + "]", self.__ol[key]): raise PermissionError
                        raise EOFError
                raise PermissionError
        except StopIteration:
            return True
        except PermissionError:
            _rrc.close()
            return False
        except EOFError:
            _rrc.close()
            return True
        finally:
            if not _configured and user:
                LOGS_.blackbox.logg(30, CNF.STRINGS.ENDIF % 'BOARD_CALL_RULE', ip=user, ico=CNF.PRINT_ICOS.rc, ansi=CNF.MSG_ANSI.yellow, mt=self._read_rule)

    def wrapper_call__(self, clear_cache:bool=False):
        wrapper_info = self._read_rule.cache_info()
        _info = f"({wrapper_info=},{self.call_cache=})"
        if clear_cache:
            self._read_rule.cache_clear()
            self.call_cache.clear()
        return _info

    def call(self, __header:[StreamHeader, ParseStreamHeader], __o, **kwargs):
        ip = self._client_set.copy().pop()[0]
        count, verified, user = self._client_cache.get(ip)
        _m, _el, self.__ol = __header.method, __header.option, __header.option_liev
        LOGS_.call.logg(10, CNF.STRINGS.IP_BOARD_PASSED % (user, self.wrapper_call__()), ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.quest)

        if search(self.drop, _m):
            LOGS_.call.logg(30, CNF.STRINGS.CALL_DROP % __header.header, ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.drop)
            raise PermissionError

        if user is None:
            if verified:
                LOGS_.call.logg(10, __o, mt=self.call, ico=CNF.PRINT_ICOS.call)
                return __o.__call__(**kwargs)
            if search(self._none_accept, _m):
                LOGS_.call.logg(10 + CNF.SIDE_[True] * 15, __o, ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.call)
                return __o.__call__(**kwargs)
            LOGS_.call.logg(30, CNF.STRINGS.CALL_DROP % __header.header, ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.drop)
            raise PermissionError

        if self._read_rule(user, _m, _el):
            _m = _m.decode(CNF.SRM_ENC)
            if user in self.call_cache and _m in self.call_cache[user]:
                lim = self.call_cache[user][_m]
                if lim[1] == lim[0]:
                    LOGS_.call.logg(40, CNF.STRINGS.CALL_LIM % (__o, lim), ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.drop)
                    raise PermissionError
                self.call_cache[user][_m][1] += 1
            LOGS_.call.logg(20, __o, ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.call)
            return __o.__call__(**kwargs)
        LOGS_.call.logg(30, CNF.STRINGS.CALL_DROP % __header.header, ip=ip, cache=self._client_cache, mt=self.call, ico=CNF.PRINT_ICOS.drop)
        raise PermissionError


########################################################################################################################
########################################################################################################################


class SimpleFireWall:

    def __init__(self):

        self._defifendifFW = DefIfEndIf(CNF.BOARD_CLIENT_RULE, *CNF.IFDEFENDIF['BOARD_CLIENT_RULE'])
        self.client_cache: dict[str: list[int, bool, str]] = dict()
        self.client_set: set[tuple] = set()
        self.client_ip: str = str()
        self.received_port: int = int()
        self.bad_client_counter = 0
        self.interval_start = int(time())

    @lru_cache(20)
    def _read_board(self, client_ip) -> bool:
        if not self._defifendifFW.configured:
            LOGS_.blackbox.logg(30, CNF.STRINGS.ENDIF % 'BOARD_CLIENT_RULE', ip=self.client_ip, cache=self.client_cache, ico=CNF.PRINT_ICOS.rc, ansi=CNF.MSG_ANSI.yellow, mt=self._read_board)
            return True
        _rrc = self._defifendifFW.read_rc()
        _configured = False
        while True:
            try:
                ln = next(_rrc)
                ip = search(b"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ln)
                if not ip: continue
                _configured = True
                if search(ip_rex(ip.group().decode(CNF.LOC_ENC)), client_ip): raise EOFError
            except StopIteration:
                LOGS_.firewall.logg(40, CNF.STRINGS.IP % self.client_ip, ip=self.client_ip, cache=self.client_cache, mt=self._read_board, ico=CNF.PRINT_ICOS.sharp)
                self.bad_client_counter += 1
                return False
            except EOFError:
                _rrc.close()
                return True
            finally:
                if not _configured:
                    LOGS_.blackbox.logg(30, CNF.STRINGS.ENDIF % 'BOARD_CLIENT_RULE', ip=self.client_ip, cache=self.client_cache, ico=CNF.PRINT_ICOS.rc, ansi=CNF.MSG_ANSI.yellow, mt=self._read_board)

    def wrapper_ips__(self, clear_cache:bool=False):
        wrapper_info = self._read_board.cache_info()
        if clear_cache: self._read_board.cache_clear()
        return wrapper_info

    def _clean_overflow(self):
        LOGS_.blackbox.logg(54, CNF.STRINGS.OVERFLOW.join(['\n' + ip for ip in self.client_cache if not self.client_cache[ip][1]]), ip=self.client_ip, cache=self.client_cache, mt=self._clean_overflow, ico=CNF.PRINT_ICOS.sharp)
        for ip in list(self.client_cache):
            if not self.client_cache[ip][1]:
                self.client_cache.pop(ip)

    def fw_reset(self):
        for ip in list(self.client_cache):
            if not self.client_cache[ip][1]:
                self.client_cache.pop(ip)
        self.bad_client_counter = 0
        self.wrapper_ips__(clear_cache=True)

    def fw_full_reset(self):
        self.client_cache.clear()
        self.bad_client_counter = 0
        self.received_port = int()
        self.interval_start = time()
        self.client_ip = str()
        self.wrapper_ips__(clear_cache=True)

    def _check_interval(self):
        actual = time()
        if self.interval_start + CNF.FIREWALL_RESET_INTERVAL < actual:
            LOGS_.firewall.logg(20, CNF.STRINGS.FW_AUTO_RESET % (actual, self.interval_start), ip=self.client_ip, cache=self.client_cache, mt=self._check_interval, ico=CNF.PRINT_ICOS.sharp)
            self.interval_start = actual
            self.fw_reset()

    def ip_on_board(self, tox_sock) -> bool:

        legal = self._read_board(self.client_ip)
        LOGS_.firewall.logg(10, CNF.STRINGS.IP_BOARD_PASSED % (self.client_ip, self.wrapper_ips__()), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.sharp)

        self._check_interval()

        hits = self.wrapper_ips__().hits

        if not legal and hits >= CNF.MAX_BAD_CLIENT_HIT_LV3:
            LOGS_.firewall.logg(55, CNF.STRINGS.DOS % (self.client_ip, 3), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENT_HIT_EXEC_LV3)
        elif not legal and hits >= CNF.MAX_BAD_CLIENT_HIT_LV2:
            LOGS_.firewall.logg(55, CNF.STRINGS.DOS % (self.client_ip, 2), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENT_HIT_EXEC_LV2)
        elif not legal and hits >= CNF.MAX_BAD_CLIENT_HIT_LV1:
            LOGS_.firewall.logg(55, CNF.STRINGS.DOS % (self.client_ip, 1), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENT_HIT_EXEC_LV1)

        if not legal and self.bad_client_counter >= CNF.MAX_BAD_CLIENTS_LV3:
            LOGS_.firewall.logg(55, CNF.STRINGS.DDOS % (self.client_ip, 3), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENTS_EXEC_LV3)
        elif not legal and self.bad_client_counter >= CNF.MAX_BAD_CLIENTS_LV2:
            LOGS_.firewall.logg(55, CNF.STRINGS.DDOS % (self.client_ip, 2), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENTS_EXEC_LV2)
        elif not legal and self.bad_client_counter >= CNF.MAX_BAD_CLIENTS_LV1:
            LOGS_.firewall.logg(55, CNF.STRINGS.DDOS % (self.client_ip, 1), ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_BAD_CLIENTS_EXEC_LV1)

        if not legal and CNF.MAXSIZE_TOXICS:
            LOGS_.firewall.logg(54, CNF.STRINGS.TOX, ip=self.client_ip, cache=self.client_cache, mt=self.ip_on_board, ico=CNF.PRINT_ICOS.tox)
            log_bad_data(self.client_ip, tox_sock)

        return legal

    def client_is_verified(self, tox_sock=None) -> bool:

        if not self.client_ip or self.client_ip == "": return False
        self.client_cache.setdefault(self.client_ip, [0, False, None])
        if (_cc := self.client_cache.get(self.client_ip)) and _cc[1]: return True
        if not _cc: return False

        LOGS_.firewall.logg(20 + (_cc[0] > 2) * 10, CNF.STRINGS.UNVERIFIED, ip=self.client_ip, cache=self.client_cache, mt=self.client_is_verified, ico=CNF.PRINT_ICOS.sharp)

        if tox_sock and CNF.MAXSIZE_TOXICS:
            LOGS_.firewall.logg(54, CNF.STRINGS.TOX, ip=self.client_ip, cache=self.client_cache, mt=self.client_is_verified, ico=CNF.PRINT_ICOS.tox)
            log_bad_data(self.client_ip, tox_sock)

        if _cc[0] > CNF.MAX_UNVERIFIED_LV3:
            LOGS_.firewall.logg(55, CNF.STRINGS.LOGIN_LV % 3, ip=self.client_ip, cache=self.client_cache, mt=self.client_is_verified, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_UNVERIFIED_EXEC_LV3)
        elif _cc[0] > CNF.MAX_UNVERIFIED_LV2:
            LOGS_.firewall.logg(55, CNF.STRINGS.LOGIN_LV % 2, ip=self.client_ip, cache=self.client_cache, mt=self.client_is_verified, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_UNVERIFIED_EXEC_LV2)
        elif _cc[0] > CNF.MAX_UNVERIFIED_LV1:
            LOGS_.firewall.logg(55, CNF.STRINGS.LOGIN_LV % 1, ip=self.client_ip, cache=self.client_cache, mt=self.client_is_verified, ico=CNF.PRINT_ICOS.warn)
            exec(CNF.MAX_UNVERIFIED_EXEC_LV1)

        if len(self.client_cache) > CNF.MAX_CLIENT_CACHE:
            self._clean_overflow()

        return False

    def port_handshake(self, header) -> None:
        self.received_port = header.option_int


########################################################################################################################
########################################################################################################################


class Verification(SimpleFireWall):

    def __init__(self):
        SimpleFireWall.__init__(self)
        self.local_login: str = None
        self._pair_pair:tuple[str, int] = tuple()
        self._pair_parts: dict = dict()
        self.lapsdelset: set = set()

    def solve_paring(self, options, pipe):
        try:
            part = options.get("T")
            if not self._pair_parts.get(part): raise KeyError(CNF.STRINGS.fe_INVALID_PART % part)
            if search(ip_rex(self._pair_pair[0]), self.client_ip):
                if int(time()) - self._pair_pair[1] < CNF.PARING_LIFETIME:
                    self.verify()
                    with open(self._pair_parts[part], 'wb') as f:
                        for _ in CNF.BUFFER_ITER(options["l"]):
                            dat = pipe.get(CNF.DAT_SOCK_BUFFER)
                            if not dat: raise BufferError(CNF.STRINGS.fe_WRONG_LENGTH)
                            f.write(dat)
                    self._pair_parts.pop(part)
                else: raise AssertionError(CNF.STRINGS.fe_TIMEOUT % (int(time()) - self._pair_pair[1]))
            else: raise AssertionError(CNF.STRINGS.fe_COMPANION % (self._pair_pair[0], self.client_ip))
            if len(list(self._pair_parts)) == 0:
                self._pair_pair = tuple()
                raise ConnectionResetError('*pres*')
        except Exception as e:
            if e.args == ('*pres*',):
                LOGS_.firewall.logg(35, CNF.STRINGS.PARED % self.client_ip, ip=self.client_ip, cache=self.client_cache, mt=self.solve_paring, ico=CNF.PRINT_ICOS.key)
            else:
                LOGS_.firewall.logg(40 + CNF.SENSITIVE_PARING * 15, type(e), e, ip=self.client_ip, cache=self.client_cache, mt=self.solve_paring)
            self._pair_pair = (tuple() if CNF.SENSITIVE_PARING else self._pair_pair)
            self._pair_parts = (dict() if CNF.SENSITIVE_PARING else self._pair_parts)
            raise ConnectionResetError
        finally:
            del options

    def get_paring(self, options):
        try:
            if search(ip_rex(self._pair_pair[0]), self.client_ip):
                if time() - self._pair_pair[1] < CNF.PARING_LIFETIME:
                    self.login(ParseStreamHeader(options.get("T").encode(CNF.SRM_ENC)))
                    if self.client_is_verified():
                        with open(self._pair_parts['P'], "rb") as f:
                            peppers = f.read()
                        with open(self._pair_parts['H'], "rb") as f:
                            hands_table = f.read()
                        self._pair_pair = tuple()
                        return peppers, hands_table
                    raise PermissionError(CNF.STRINGS.fe_LOGIN_VERIFY)
                else: raise AssertionError(CNF.STRINGS.fe_TIMEOUT % (int(time()) - self._pair_pair[1]))
            else: raise AssertionError(CNF.STRINGS.fe_COMPANION % (self._pair_pair[0], self.client_ip))
        except Exception as e:
            LOGS_.firewall.logg(40 + CNF.SENSITIVE_PARING * 15, type(e), e, ip=self.client_ip, cache=self.client_cache, mt=self.get_paring)
        finally:
            del options
            self._pair_pair = (tuple() if CNF.SENSITIVE_PARING else self._pair_pair)
            self._pair_parts = (dict() if CNF.SENSITIVE_PARING else self._pair_parts)

    def read_hostfsc(self):
        with open(CNF.AUTH_CONF[self.client_cache[self.client_ip][2]]['ppp'], "rb") as f:
            p = f.read()
        with open(CNF.AUTH_CONF[self.client_cache[self.client_ip][2]]['hst'], "rb") as f:
            h = f.read()
        return p, h

    def verify(self, user=None):
        self.client_cache[self.client_ip][1] = self.received_port
        self.client_cache[self.client_ip][2] = user
        lv = (61 if CNF.MOD_LOGIN_TO_ALERT else 25)
        LOGS_.firewall.logg(lv, CNF.STRINGS.LOGIN % self.client_ip, ip=self.client_ip, cache=self.client_cache, mt=self.verify, ico=CNF.PRINT_ICOS.y)

    def login(self, header, change:str=False) -> tuple[bytes, bytes, int]:

        _spices: list = list()

        try:
            if change: header.option_liev['u'] = change
            if not header.option_liev.get('i'): raise AssertionError(CNF.STRINGS.fe_NO_LOGIN)
            if not header.option_liev.get('u'): raise AssertionError(CNF.STRINGS.fe_NO_USER)
            if change and not header.option_liev.get('I'): raise AssertionError(CNF.STRINGS.fe_NO_NEW_LI)
            if CNF.AUTH_CONF[header.option_liev['u']]['lpl'] == 0:
                self.lapsdelset.add(header.option_liev['u'])
                raise AssertionError(CNF.STRINGS.fe_LAPSLIN_LIM)

            with open(CNF.AUTH_CONF[header.option_liev['u']]['spc'], 'rb') as f:
                try:
                    _spices = list(FStreamCipher(
                        f.read(), header.option_liev['i'], *CNF.AUTH_CONF[header.option_liev['u']]['bpp']).decrypt(
                    ).strip().split())
                    _spices = [
                        int(_spices[0]),
                        _spices[1].decode(CNF.LOC_ENC),
                        int(_spices[2]),
                        literal_eval(_spices[3].decode(CNF.LOC_ENC)),
                        int(_spices[4])]
                except IndexError:
                    raise IndexError(CNF.STRINGS.fe_PEPPER2)
            with open(CNF.AUTH_CONF[header.option_liev['u']]['lin'], 'rb') as f:
                
                if FStreamCipher(
                        f.read(), _spices.pop(1) + header.option_liev['i'], *_spices[1:]
                ).decrypt() != header.option_liev['i'].encode(CNF.SRM_ENC):
                    self.client_cache[self.client_ip][1] = False
                    raise AssertionError(CNF.STRINGS.fe_LOGIN_VERIFY)

            if _spices.pop(0) + CNF.AUTH_CONF[header.option_liev['u']]['lft'] < time() and not change:
                CNF.AUTH_CONF[header.option_liev['u']]['lpl'] += 1
                if CNF.AUTH_CONF[header.option_liev['u']]['lpd']:
                    CNF.AUTH_CONF[header.option_liev['u']]['lpd'] = 0
                    _rcDELUser(header.option_liev['u'])
                lapsed = 1
                LOGS_.firewall.logg(30, CNF.STRINGS.LOGIN_LAPSED, ip=self.client_ip, cache=self.client_cache, mt=self.login, ico=CNF.PRINT_ICOS.key, ansi=CNF.MSG_ANSI.underline)
            else:
                lapsed = 0

            self.verify(header.option_liev['u'])

            with open(CNF.AUTH_CONF[header.option_liev['u']]['hst'], 'rb') as f:

                d = strftime("%d", gmtime(time()))
                H = strftime("%H", gmtime(time()))

                _verified = 1
                return FStreamCipher(
                    f.read(), header.option_liev['i'], *_spices
                ).decrypt().splitlines()[int(d) - 1].split()[int(H)], (d + H).encode(CNF.SRM_ENC), lapsed

        except (ValueError, SyntaxError) as e:
            LOGS_.firewall.logg(40, type(e), e, CNF.STRINGS.fe_PEPPER, ip=self.client_ip, cache=self.client_cache, mt=self.login, ico=CNF.PRINT_ICOS.exclam2)
            return b'', b'', 0
        except IndexError as e:
            LOGS_.firewall.logg(60, type(e), e, CNF.STRINGS.fe_PEPPER2, mt=self.login, ico=CNF.PRINT_ICOS.exclam2)
            return b'', b'', 0
        except AssertionError as e:
            LOGS_.firewall.logg(40, type(e), e, ip=self.client_ip, cache=self.client_cache, mt=self.login, ico=CNF.PRINT_ICOS.exclam2)
            return b'', b'', 0
        except (AttributeError, KeyError) as e:
            LOGS_.firewall.logg(40, type(e), e, CNF.STRINGS.fe_NO_LOGIN, ip=self.client_ip, cache=self.client_cache, mt=self.login, ico=CNF.PRINT_ICOS.quest)
            return b'', b'', 0
        finally:
            try:
                del _verified
            except UnboundLocalError:
                pass
            else:
                if self.client_is_verified() and change:
                    mk_login(header.option_liev['u'], header.option_liev['I'])
                    _rcUDELUser(header.option_liev['u'])
            del header.option_liev
            header = None
            _spices.clear()

    def login_shake(self, header) -> None:

        _peppers: list = list()

        def verify_time(day, hour):
            t = gmtime(time())
            c = timegm(strptime(f"{t.tm_year} {t.tm_mon} {day} {hour} {t.tm_min} {t.tm_sec}", "%Y %m %d %H %M %S"))
            age = timegm(gmtime(time())) - c
            if timegm(gmtime(time())) - c > CNF.TIMESTAMP_LIFETIME:
                raise AssertionError(CNF.STRINGS.fe_TIMESTAMP % (CNF.TIMESTAMP_LIFETIME, age))

        try:
            if not self.local_login: raise AssertionError(CNF.STRINGS.fe_NO_LLOGIN)
            verify_time(header.option_liev['t'][:2], header.option_liev['t'][2:])
            with open(CNF.AUTH_CONF[None]['spc'], "rb") as f:
                _peppers = list(FStreamCipher(f.read(), self.local_login, *CNF.BASIC_FSC_PEPPER).decrypt().strip().split())
                _peppers[0], _peppers[1], _peppers[2] = int(_peppers[0]), (
                    int(_peppers[1]), int(_peppers.pop(2))), int(_peppers[2])
            with open(CNF.AUTH_CONF[None]['hst'], "rb") as f:
                if FStreamCipher(
                        f.read(), self.local_login, *_peppers
                    ).decrypt().splitlines()[
                    int(header.option_liev['t'][:2]) - 1
                ].split()[int(header.option_liev['t'][2:])] != header.option_liev['h'].encode(CNF.SRM_ENC):
                    raise AssertionError(CNF.STRINGS.fe_HANDSHAKE)
            self.verify()
            if header.option_liev['L']:
                LOGS_.firewall.logg(30, CNF.STRINGS.LOGIN_LAPSED, ip=self.client_ip, cache=self.client_cache, mt=self.login_shake, ico=CNF.PRINT_ICOS.key, ansi=CNF.MSG_ANSI.underline)
        except ValueError as e:
            LOGS_.firewall.logg(40, type(e), e, CNF.STRINGS.fe_CAST, header.header, ip=self.client_ip, cache=self.client_cache, mt=self.login_shake, ico=CNF.PRINT_ICOS.exclam2)
        except AssertionError as e:
            LOGS_.firewall.logg(40, type(e), e, header.header, ip=self.client_ip, cache=self.client_cache, mt=self.login_shake, ico=CNF.PRINT_ICOS.exclam2)
        except KeyError as e:
            LOGS_.firewall.logg(40, type(e), e, CNF.STRINGS.fe_KEY_MISSING, header.header, ip=self.client_ip, cache=self.client_cache, mt=self.login_shake, ico=CNF.PRINT_ICOS.quest)
        except IndexError as e:
            LOGS_.firewall.logg(40, type(e), e, CNF.STRINGS.fe_TABLE, header.header, ip=self.client_ip, cache=self.client_cache, mt=self.login_shake, ico=CNF.PRINT_ICOS.exclam2)
        finally:
            _peppers.clear()
            del header.option_liev
            self.local_login = None
            header = None


########################################################################################################################
########################################################################################################################


class SecurePath:

    def __init__(self, client_cache:dict):

        self.user = list(client_cache.values())[0][2]
        if self.user is not None: self.user = self.user.encode(CNF.LOC_ENC)

        self._defifendifSP = DefIfEndIf(CNF.BOARD_PATH_RULE, *CNF.IFDEFENDIF['BOARD_PATH_RULE'])

        self.SRCDST: dict = {
            'src': {'root': CNF.SRC_BASIC_ROOT + '/', 'current': CNF.SRC_BASIC_ROOT + '/', 'black': str(), 'white': str()},
            'dst': {'root': CNF.DST_BASIC_ROOT + '/', 'current': CNF.DST_BASIC_ROOT + '/', 'black': str(), 'white': str()}
        }

        self.read_file = 4
        self.read_dir = 5
        self.write_dir = 3

        try:
            _rrc = self._defifendifSP.read_rc()
        except AssertionError:
            pass

        while True:
            if self.user is None: break
            if not self._defifendifSP.configured:
                break
            try:
                ln = next(_rrc).strip()
                if not search(b"^" + self.user + b" // ([sSpP][wWbB]|[wWbB][sSpP]) // .+", ln): continue
                conf = ln.decode(CNF.LOC_ENC).split(' // ')
                conf[1] = conf[1].lower()
                if 's' in conf[1] and 'b' in conf[1]:
                    if conf[2].endswith('//'):
                        self.SRCDST['src']['black'] += '^' + escape(self.realpath(conf[2])) + '(/[^/]*$|$)|'
                    else: self.SRCDST['src']['black'] += '^' + escape(self.realpath(conf[2])) + '|'
                if 's' in conf[1] and 'w' in conf[1]:
                    if conf[2].endswith('//'):
                        self.SRCDST['src']['white'] += '^' + escape(self.realpath(conf[2])) + '(/[^/]*$|$)|'
                    else: self.SRCDST['src']['white'] += '^' + escape(self.realpath(conf[2])) + '|'
                if 'p' in conf[1] and 'b' in conf[1]:
                    if conf[2].endswith('//'):
                        self.SRCDST['dst']['black'] += '^' + escape(self.realpath(conf[2])) + '(/[^/]*$|$)|'
                    else: self.SRCDST['dst']['black'] += '^' + escape(self.realpath(conf[2])) + '|'
                if 'p' in conf[1] and 'w' in conf[1]:
                    if conf[2].endswith('//'):
                        self.SRCDST['dst']['white'] += '^' + escape(self.realpath(conf[2])) + '(/[^/]*$|$)|'
                    else: self.SRCDST['dst']['white'] += '^' + escape(self.realpath(conf[2])) + '|'
            except StopIteration:
                break

        if self.SRCDST['src']['black']: self.SRCDST['src']['black'] = self.SRCDST['src']['black'][:-1]
        if self.SRCDST['src']['white']: self.SRCDST['src']['white'] = self.SRCDST['src']['white'][:-1]
        if self.SRCDST['dst']['black']: self.SRCDST['dst']['black'] = self.SRCDST['dst']['black'][:-1]
        if self.SRCDST['dst']['white']: self.SRCDST['dst']['white'] = self.SRCDST['dst']['white'][:-1]

        if self.user and not self.SRCDST['src']['black'] and not self.SRCDST['dst']['black'] \
                     and not self.SRCDST['src']['white'] and not self.SRCDST['dst']['white']:
            LOGS_.blackbox.logg(30, CNF.STRINGS.ENDIF % 'BOARD_PATH_RULE', ip=self.user.decode(CNF.LOC_ENC), ico=CNF.PRINT_ICOS.rc, ansi=CNF.MSG_ANSI.yellow, mt=self.__init__)
            LOGS_.path.logg(30, CNF.STRINGS.ENDIF % 'BOARD_PATH_RULE', ip=self.user.decode(CNF.LOC_ENC), mt=self.__init__, ico=CNF.PRINT_ICOS.stacks)
        elif self.user:
            LOGS_.path.logg(25, CNF.STRINGS.SECUREPATH % self.user.decode(CNF.LOC_ENC), ip=self.user.decode(CNF.LOC_ENC), mt=self.__init__, ico=CNF.PRINT_ICOS.stacks)

    @staticmethod
    def realpath(path: str):
        _realpath = os_path.realpath(path)
        if CNF.SYS_PLATFORM == "w":
            return subwinpath(_realpath)
        return _realpath

    @staticmethod
    def realdst(path: str):
        if path is False:
            return False
        if CNF.SYS_PLATFORM == "w":
            return subwininval(path)
        return path

    def _parse_path(self, path: str, key: str) -> str:
        return self.realpath(
            (CNF.HOME_PATH + path[3:] if path.startswith('~//') else
             self.SRCDST[key]['root'] + path[3:] if path.startswith('#//') else
             self.SRCDST[key]['current'] + path if not path.startswith(CNF.SYS_ROOT) else
             path))

    def _legal(self, path: str, key: str) -> [str, False]:
        if not path: return False
        legal = True
        if self.SRCDST[key]['white']:
            legal = search(self.SRCDST[key]['white'], path)
            if not legal:
                LOGS_.path.logg(40, path, mt=self._legal, ico=CNF.PRINT_ICOS.wstacks)
                return False
        if self.SRCDST[key]['black']:
            legal = True ^ bool(search(self.SRCDST[key]['black'], path))
        if legal:
            LOGS_.path.logg(20, path, mt=self._legal, ico=CNF.PRINT_ICOS.stacks)
            return path
        LOGS_.path.logg(40, path, mt=self._legal, ico=CNF.PRINT_ICOS.bstacks)
        return False

    def src_f_path(self, path: str) -> [str, False]:
        path = self._parse_path(path, 'src')
        if not access(path, self.read_file):
            LOGS_.path.logg(30, path, mt=self.src_f_path, ico=CNF.PRINT_ICOS.stacks)
            return False
        return self._legal(path, 'src')

    def src_l_path(self, path: str) -> [str, False]:
        path = self._legal(self._parse_path(path, 'src'), 'src')
        if not path: return False
        if not access(path, self.read_dir):
            LOGS_.path.logg(30, path, mt=self.src_l_path, ico=CNF.PRINT_ICOS.stacks)
            return False
        if path:
            if os_path.isdir(path): return path
            return sub('/[^/]*$', '', path)
        return False

    def dst_path(self, path: str) -> [str, False]:
        path = self.realdst(self._parse_path(path, 'dst'))
        if not access(sub('/[^/]*$', '/', path), self.write_dir):
            LOGS_.path.logg(30, path, mt=self.dst_path, ico=CNF.PRINT_ICOS.stacks)
            return False
        return self._legal(path, 'dst')

    def dst_secure_path(self, path: str) -> [str, False]:
        path = self.dst_path(path)
        if path:
            if os_path.lexists(path):
                LOGS_.path.logg(30, path, mt=self.dst_secure_path, ico=CNF.PRINT_ICOS.stacks)
                raise FileExistsError
            return path
        return False

    def dst_a(self, path: str) -> [str, False]:
        path = self.realdst(self._legal(self._parse_path(path, 'dst'), 'dst'))
        if path:
            makedirs(sub('/[^/]*$', '/', path), 0o770, exist_ok=True)
            return path
        return False

    def dst_secure_a(self, path: str) -> [str, False]:
        path = self.realdst(self._legal(self._parse_path(path, 'dst'), 'dst'))
        if path:
            if os_path.lexists(path):
                LOGS_.path.logg(30, path, mt=self.dst_secure_a, ico=CNF.PRINT_ICOS.stacks)
                raise FileExistsError
            makedirs(sub('/[^/]*$', '/', path), 0o770, exist_ok=True)
            return path
        return False

    def cd_src(self, path: str) -> bool:
        path = self._legal(self._parse_path(path, 'src'), 'src')
        if path:
            if os_path.isdir(path) and access(path, self.read_dir):
                self.SRCDST['src']['current'] = path + '/'
                return True
            path = sub('/[^/]*$', '/', path)
            if access(path, self.read_dir):
                self.SRCDST['src']['current'] = path
                return True
        LOGS_.path.logg(10, path, mt=self.cd_src, ico=CNF.PRINT_ICOS.stacks)
        return False

    def cd_dst(self, path: str) -> bool:
        path = self._legal(self._parse_path(path, 'dst'), 'dst')
        if path:
            if os_path.isdir(path) and access(path, self.write_dir):
                self.SRCDST['dst']['current'] = path + '/'
                return True
            path = sub('/[^/]*$', '/', path)
            if access(path, self.write_dir):
                self.SRCDST['dst']['current'] = path
                return True
        LOGS_.path.logg(10, path, mt=self.cd_dst, ico=CNF.PRINT_ICOS.stacks)
        return False

    def assifnodst(self, src: str, dst: str):
        dst = self._parse_path(dst, 'dst')
        if os_path.isdir(dst := dst + '/'):
            dst += search("[^/]*$", src).group()
        return dst

    def rassifnodst(self, src: str, dst: str):
        if not dst or dst.endswith('/'):
            dst += search("[^/]*$", src).group()
        return dst
