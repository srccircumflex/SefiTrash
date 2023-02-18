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


from sys import stderr, stdout, platform, getfilesystemencoding
from os import environ, access, scandir
from os import path as os_path
from ast import literal_eval
from re import search, sub
from time import time

from sec.fTools import DefIfEndIf, getpublicip, getlocalip, subwinpath
from _rc import configurations
from sec.fscIO import pph


configurations.SYS_PLATFORM = ("w" if platform == "win32" else "l")

class IPValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class FSCValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class PairingValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class InterveneValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class InspectValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class MailValueError(ValueError):
    def __init__(self, *args):
        ValueError.__init__(*args)

class GetFromIfFromSubClass:
    cache = dict()

    def __call__(self, __attr:str, ___attr:str):
        if __attr not in configurations.FROM_SUBCLASS:
            return __attr
        self.cache.setdefault(
            __attr,
            getattr(
                __import__('_rc._defaults_', globals(), locals(), [''], 0),
                __attr
            )()
        )
        return getattr(self.cache[__attr], ___attr)

GetFromIfFromSubClass = GetFromIfFromSubClass()

def _mk_defaults():
    for conf in configurations.__dir__():
        if conf == 'EOF': break
        if conf.startswith("__"): continue
        if getattr(configurations, conf) is None:
            _default = getattr(
                __import__('_rc._defaults_', globals(), locals(), [''], 0),
                conf.lower()
            )
            _default = GetFromIfFromSubClass(_default, conf.lower())
            setattr(configurations, conf, _default)

def _setfromrcfile(_file):
    _ifdefs = list()
    _endifs = list()
    for board in configurations.IFDEFENDIF:
        if DefIfEndIf(_file,
                      *configurations.IFDEFENDIF[board]).configured:
            setattr(configurations, board, _file)
            _ifdefs.append(configurations.IFDEFENDIF[board][0].replace(b' ', b'').decode('utf8'))
            _endifs.append(configurations.IFDEFENDIF[board][1].replace(b' ', b'').decode('utf8'))
    with open(_file) as f:
        n_lines = range(f.read().count('\n') + 1)
    with open(_file) as f:
        for _ in n_lines:
            ln = f.readline()
            if ln.replace(' ', '') in _ifdefs:
                _ifdefs.remove(ln.replace(' ', ''))
                while True:
                    ln = f.readline()
                    if ln.replace(' ', '') in _endifs:
                        _endifs.remove(ln.replace(' ', ''))
                        break
            if ln.startswith('#'): continue
            if not ln: continue
            _attr = search("^\w+", ln)
            if _attr:
                _attr = _attr.group()
                if not hasattr(configurations, _attr):
                    raise AttributeError(f"NoConfigurationAttribute : '{_attr}'")
                _val = sub(_attr + "\s*:?[^=]*=\s*", "", ln)
                _val = literal_eval(_val)
                _val = GetFromIfFromSubClass(_val, _attr.lower())
                setattr(configurations, _attr, _val)

def _read_ifhomerc():
    if configurations.SYS_PLATFORM == "w":
        if access((_u_rc := environ['HOMEPATH'] + configurations.wU_RC), 4):
            configurations.RC_FILE_LV1 = _u_rc
    else:
        if access((_u_rc := environ['HOME'] + configurations.lU_RC), 4):
            configurations.RC_FILE_LV1 = _u_rc
    if configurations.RC_FILE_LV1 and access(configurations.RC_FILE_LV1, 4):
        _setfromrcfile(configurations.RC_FILE_LV1)

def _read_ifurc():
    if configurations.USER is None:
        if configurations.DEFAULT_USER is None: raise AssertionError("no user")
        configurations.USER = configurations.DEFAULT_USER
    if access(configurations.MAIN_ROOT + '/etc', 5):
        _scan = scandir(configurations.MAIN_ROOT + '/etc')
        while True:
            try:
                _entry = next(_scan).path
                if search("[/\\\]" + configurations.USER + "\.[^/\\\]*$", _entry) and access(_entry, 4):
                    _setfromrcfile(_entry)
            except StopIteration:
                break

def _set_localipparsif():
    if configurations.IP_LOCAL.startswith('get'):
        _cmd = configurations.IP_LOCAL.split()
        if _cmd[1] == 'local':
            if len(_cmd) > 2 and _cmd[2] == 'from':
                configurations.IP_LOCAL = getlocalip(
                    search("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", configurations.IP_LOCAL).group()
                )
            else:
                configurations.IP_LOCAL = getlocalip()
        elif _cmd[1] == 'public':
            configurations.IP_LOCAL = getpublicip()
        else:
            raise SyntaxError(f"IP_LOCAL: cant parse second in ip: '{_cmd[1]}'\n"
                              f"use 'get local', 'get local from <[dns]ip>' or 'get public'")
    if not search("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", configurations.IP_LOCAL):
        raise IPValueError(f"IP_LOCAL: <invalid '{configurations.IP_LOCAL}'>")

def _parsbpp(ln:str, fromuserln:str=None):
    if fromuserln is None: user = 'x'; ln = 'x bpp:' + ln
    else: user = fromuserln
    if _bpp := search("(?<=" + user + ")\s+.*bpp:[1-9]\d{0,2}[+-][1-9]\.[1-9]", ln):
        _bpp = _bpp.group()
        return (int(search("(?<=bpp:)\d+(?=[+-])", _bpp).group()),
                ({"+": 1, "-": 0}.get(search("[+-]", _bpp).group()),
                int(search("(?<=[+-])\d+(?=\.)", _bpp).group())),
                int(search("(?<=\.)\d+", _bpp).group()))

def _buildpp(inp):
    _o = None
    if inp is None: raise AttributeError("cant parse 'None'")
    if isinstance(inp, str):
        _o = _parsbpp(inp)
    else: _o = inp
    if isinstance(_o, tuple):
        try:
            if _o[0] not in range(0, 1000): raise FSCValueError("<IV> not in range(1-999)")
            if _o[1][0] not in (0, 1): raise FSCValueError("<part> not bit compatible")
            if _o[1][1] not in range(1, 10): raise FSCValueError("<prio> not in range(1-9)")
            if _o[2] not in range(1, 10): raise FSCValueError("<hops> not in range(1-9)")
        except IndexError: raise SyntaxError(f"{inp} => {_o}")
    else: raise SyntaxError(f"{inp} => {_o}")
    return _o

def _build_hostd():

    configurations.BASIC_FSC_PEPPER = _buildpp(configurations.BASIC_FSC_PEPPER)

    configurations.AUTH_CONF = {None: {
        'hst': configurations.FSC_ESTABLISH_TABLE_FILE % configurations.USER,
        'spc': configurations.FSC_ESTABLISH_PEPPER % configurations.USER}}

def _build_clientd():

    configurations.BASIC_FSC_PEPPER = _buildpp(configurations.BASIC_FSC_PEPPER)

    configurations.AUTH_CONF = dict()

    for user in {configurations.DEFAULT_USER, configurations.USER}:
        if user is None: continue
        configurations.AUTH_CONF |= {user: {
            'spc': configurations.FSC_HOST_SPICE_FILE % user,
            'lin': configurations.FSC_HOST_XF % user,
            'hst': configurations.FSC_HOST_TABLE_FILE % user,
            'ppp': configurations.FSC_PEPPER_HOST % user,
            'lft': configurations.FSC_XF_LIFETIME,
            'lpl': ~configurations.LAPSLOGIN_LIM_RUNTIME,
            'lpd': configurations.LAPSLOGIN_DEL,
            'bpp': configurations.BASIC_FSC_PEPPER
        }}

    def defif(file): return DefIfEndIf(file, *configurations.IFDEFENDIF['BOARD_USERS']).read_rc()

    _defif = defif(configurations.BOARD_USERS)
    _deffor = set()

    def deffor(user, ln):
        if bpp := _parsbpp(ln, user): return bpp
        else:
            _deffor.add(user)
            return None

    while True:
        try:
            _user_ln = next(_defif).decode(configurations.LOC_ENC)
            if user := search("^\w+(?=\s)", _user_ln):
                if '<del>' in _user_ln:
                    print(f"del {user=}", file=stderr)
                    continue
                user = user.group()
                if lft := search("(?<=" + user + ")\s+.*lft:\d+", _user_ln):
                    lft = int(search("lft:\d+", lft.group()).group()[4:])
                else: lft = configurations.FSC_XF_LIFETIME
                if lpl := search("(?<=" + user + ")\s+.*lpl:\d+", _user_ln):
                    lpl = ~int(search("lpl:\d+", lpl.group()).group()[4:])
                else: lpl = ~configurations.LAPSLOGIN_LIM_RUNTIME
                if lpd := search("(?<=" + user + ")\s+.*lpd:\d", _user_ln):
                    lpd = int(search("lpd:\d", lpd.group()).group()[4:])
                else: lpd = configurations.LAPSLOGIN_DEL

                configurations.AUTH_CONF |= {user: {
                    'spc': configurations.FSC_HOST_SPICE_FILE % user,
                    'lin': configurations.FSC_HOST_XF % user,
                    'hst': configurations.FSC_HOST_TABLE_FILE % user,
                    'ppp': configurations.FSC_PEPPER_HOST % user,
                    'lft': lft,
                    'lpl': lpl,
                    'lpd': lpd,
                    'bpp': deffor(user, _user_ln)
                }}
        except StopIteration:
            break

    while _deffor:
        print(f"{_deffor=}", file=stderr)
        print("|[ <IV=(0-999)><part=[+-]><prio=(1-9)>.<hops=(1-9)> ]|[ read:<file> ]|[ defaults ]|", file=stderr)

        for _ in _deffor.copy():
            user = _deffor.pop()
            if user in configurations.AUTH_CONF and configurations.AUTH_CONF[user]['bpp']:
                continue
            inp = input(f"[{user}]: ")
            if inp.replace(' ', '') == 'defaults':
                configurations.BASIC_FSC_PEPPER = _buildpp(configurations.BASIC_FSC_PEPPER)
                bpp = configurations.BASIC_FSC_PEPPER
            elif _read := search("^\s*read:\s*", inp):
                if access((_file := search("(?<=" + _read.group() + ").*", inp).group()), 4):
                    _defif = defif(_file)
                    while True:
                        try:
                            _user_ln = next(_defif).decode(configurations.LOC_ENC)
                            if user := search("^\w+(?=\s)", _user_ln):
                                user = user.group()
                                if '<del>' in _user_ln:
                                    print(f"del {user=}", file=stderr)
                                    continue
                                try:
                                    configurations.AUTH_CONF[user]['bpp'] = deffor(user, _user_ln)
                                except KeyError:
                                    print(f"KeyError {user=} ?<del>", file=stderr)
                        except StopIteration:
                            break
                else: raise FileNotFoundError(f"{_file=}")
                break
            else:
                bpp = deffor(user, f"{user} bpp:{inp.replace(' ', '')}")

            configurations.AUTH_CONF[user]['bpp'] = bpp

def _buildiplist():
    if type(configurations.IP_RECEIVER) == str:
        configurations.IP_RECEIVER = [configurations.IP_RECEIVER]
    if type(configurations.IP_RECEIVER) != list:
        configurations.IP_RECEIVER = list(configurations.IP_RECEIVER)

    def _mkiplist():
        for _i in range(len(configurations.IP_RECEIVER)):
            _ran = search("[0-9]{1,3}-[0-9]{1,3}", configurations.IP_RECEIVER[_i])
            if _ran:
                a = _ran.start()
                z = _ran.end()
                _ran = _ran.group().split('-')
                for _p in range(int(_ran[0]), int(_ran[1]) + 1):
                    configurations.IP_RECEIVER.append(
                        configurations.IP_RECEIVER[_i][:a] + str(_p)
                        + configurations.IP_RECEIVER[_i][z:]
                    )
                configurations.IP_RECEIVER.pop(_i)
                _mkiplist()
    _mkiplist()
    for ip in configurations.IP_RECEIVER:
        if not search("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip):
            raise IPValueError(f"IP_RECEIVER: <invalid '{ip=}'>")

def _build_attr():
    # CODING
    for c in ('LOC_ENC', 'LOG_ENC', 'SRM_ENC'):
        if not getattr(configurations, c):
            setattr(configurations, c, getfilesystemencoding())
        str().encode(getattr(configurations, c))
    if configurations.CLIENT_SIDE and not configurations.LATERAL_:
        # IP RANGE
        _buildiplist()
        # PORT RANGES
        if not isinstance(configurations.PORT_RANGE_ESTABLISH, (tuple, list)): raise AttributeError(str(configurations.PORT_RANGE_ESTABLISH))
        # default IO-STREAM
        configurations._BYPASSED = stdout
    if configurations.HOST_SIDE and not configurations.LATERAL_:
        # PARING
        if configurations.PROVIDED_PARING_USER and configurations.PROVIDED_PARING_IP:
            configurations.PROVIDED_PARING = [
                configurations.PROVIDED_PARING_USER,
                (configurations.PROVIDED_PARING_IP, time())
            ]
        elif configurations.PROVIDED_PARING_IP:
            raise PairingValueError('PROVIDED_PARING: <ip without user>')
        elif configurations.PROVIDED_PARING_USER:
            raise PairingValueError('PROVIDED_PARING: <user without ip>')
        else:
            configurations.PROVIDED_PARING = None
    if configurations.HOST_SIDE:
        # INTERVENT
        if configurations.INTERVENT_IP and configurations.INTERVENT_PORT:
            configurations.INTERVENT_BINDING = (
                configurations.INTERVENT_IP, configurations.INTERVENT_PORT
            )
        elif configurations.INTERVENT_PORT:
            raise InterveneValueError('INTERVENT: <port without ip>')
        elif configurations.INTERVENT_IP:
            raise InterveneValueError('INTERVENT: <ip without port>')
        else:
            configurations.INTERVENT_BINDING = None
    if not configurations.LATERAL_:
        configurations.SIDE_ = {configurations.HOST_SIDE: 1, configurations.CLIENT_SIDE: 0}
        # PORT RANGES
        if not isinstance(configurations.PORT_RANGE_RECEIVER, (tuple, list)): raise AttributeError(str(configurations.PORT_RANGE_RECEIVER))
        # MODIFY LOG LEVELS IF MOD
        _loglvs = [
            configurations.LOGLV_PATH,
            configurations.LOGLV_CALL,
            configurations.LOGLV_KILL,
            configurations.LOGLV_BRIDGE,
            configurations.LOGLV_SOCKIO,
            configurations.LOGLV_FIREWALL,
            configurations.LOGLV_BLACKBOX
        ]
        if configurations.MOD_LOGLVTO_DEBUG:
            for _lvl in _loglvs:
                _lvl[0] = 0
        if configurations.MOD_LOGLVTO_BLACKBOX:
            configurations.LOGLV_BLACKBOX[1] = 0
        if configurations.MOD_LOGLVTO_ALLS is not None and not isinstance(configurations.MOD_LOGLVTO_ALLS, bool):
            for _lvl in _loglvs:
                _lvl[0] = configurations.MOD_LOGLVTO_ALLS
        if configurations.MOD_LOGLVTO_ALLF is not None and not isinstance(configurations.MOD_LOGLVTO_ALLF, bool):
            for _lvl in _loglvs:
                _lvl[1] = configurations.MOD_LOGLVTO_ALLF
    # INSPECT
    if configurations.INSPECT_IP and configurations.INSPECT_PORT:
        configurations.INSPECT_BINDING = (
            configurations.INSPECT_IP, configurations.INSPECT_PORT
        )
    elif configurations.INSPECT_PORT:
        raise InspectValueError('INSPECT: <port without ip>')
    elif configurations.INSPECT_IP:
        raise InspectValueError('INSPECT: <ip without port>')
    else:
        configurations.INTERVENT_BINDING = None
    # STREAM FORMAT
    configurations.STREAM_FORMAT, configurations.MSG_ANSI, configurations.LEVEL_TO_ANSI_PREFIX, configurations.LEVEL_TO_ANSI_NAME = configurations.PRINT_STREAM_ARGS

    if configurations.SYS_PLATFORM == "w":
        from signal import SIGINT, SIGBREAK, SIGTERM
        configurations.SIG_SEQ = [SIGINT, SIGBREAK, SIGTERM]    # [2,21,15]
        configurations.SYS_ROOT = subwinpath(os_path.realpath(environ['HOMEPATH']))
        configurations.HOME_PATH = subwinpath(os_path.realpath(environ['HOMEPATH'])) + '/'
        if configurations.MOD_BGSTREAM is None: configurations.MOD_BGSTREAM = False
        if not configurations.HOST_SIDE: configurations.MOD_BGSTREAM = None
    else:
        from signal import SIGINT, SIGTERM, SIGKILL
        configurations.SIG_SEQ = [SIGTERM, SIGKILL]             # [-15,-9]
        configurations.SYS_ROOT = '/'
        configurations.HOME_PATH = environ['HOME'] + '/'
        if configurations.MOD_BGSTREAM is None: configurations.MOD_BGSTREAM = True
        if not configurations.HOST_SIDE: configurations.MOD_BGSTREAM = None

def _check_faccess():
    if configurations.LATERAL_:
        _drequired = {}
        _frequired = {'^log_': 2, '^log_kill$': 6}
        _frequirow = {'^log_': 3, '^log_kill$': 3}
    elif configurations.CLIENT_SIDE:
        _drequired = {'^logpath': 3, '^src': 5, '^dst': 3}
        _frequired = {'^ssl': 4, '^log_': 2, '^log_kill$': 6}
        _frequirow = {'^log_': 3, '^log_kill$': 3}
        _auths = ('spc', 'hst')
    elif configurations.HOST_SIDE:
        _drequired = {'^logpath': 3, '^src': 5, '^dst': 3}
        _frequired = {'^ssl': 4, '^board': 4, '^board_users$': 6, '^log_': 2, '^log_kill$': 6}
        _frequirow = {'^log_': 3, '^log_kill$': 3}
    for _kw in __import__(
            '_rc._file_conf', globals(), locals(), [''], 0).__class__.__dir__(
            __import__('_rc._file_conf', globals(), locals(), [''], 0)):
        if _kw.startswith('_'): continue
        _attr = getattr(configurations, _kw.upper())
        if _attr is None: _attr = os_path.devnull
        _attr = os_path.realpath(_attr)
        if platform == "win32": _attr = subwinpath(_attr)
        setattr(configurations, _kw.upper(), _attr)
        for _re in _frequired:
            if search(_re, _kw):
                if os_path.isdir(_attr): raise IsADirectoryError(f"{_attr}")
                if os_path.isfile(_attr) or _attr == os_path.devnull:
                    if not access(_attr, _frequired[_re]):
                        raise PermissionError(f"{_attr}")
                elif _re not in _frequirow: raise FileNotFoundError(f"{_attr}")
                if _re in _frequirow:
                    if _attr == os_path.devnull or _kw.upper() == 'LOG_BASIC_FILE': continue
                    if not os_path.isdir((_path := sub("/[^/]*$", "", _attr))):
                        raise FileNotFoundError(f"{_attr}")
                    elif not access(_path, _frequirow[_re]):
                        raise PermissionError(f"{_path}")
        for _re in _drequired:
            if search(_re, _kw) and (not os_path.isdir(_attr) or not access(_attr, _drequired[_re])):
                raise NotADirectoryError(f"{_attr}")

def _check_authaccess():
    if configurations.CLIENT_SIDE:
        _auths = ('spc', 'hst')
        _authow = (() if not configurations.DO_PAR else _auths)
    elif configurations.HOST_SIDE:
        _auths = ('spc', 'lin', 'hst')
        _authow = ('ppp',)
    for _userauth in configurations.AUTH_CONF:
        for _auth in configurations.AUTH_CONF[_userauth]:
            if _auth in _auths and os_path.isfile(configurations.AUTH_CONF[_userauth][_auth]):
                if not access(configurations.AUTH_CONF[_userauth][_auth], 6):
                    raise PermissionError(f"{configurations.AUTH_CONF[_userauth][_auth]}")
            elif _auth in _authow and os_path.isdir((_path := sub("/[^/]*$", "", configurations.AUTH_CONF[_userauth][_auth]))):
                if not access(_path, 7):
                    raise PermissionError(f"{_path}")


def _mailalert_defif() -> bool:
    if access(configurations.MAIL_XF % configurations.USER, 4):
        _required = {'MAIL_SMTP_ADDR', 'MAIL_SMTP_PORT', 'MAIL_CRYPT', 'MAIL_SENDER_MAIL'}
        for req in _required.copy():
            if isinstance(_attr := getattr(configurations, req), bool) or _attr is None: continue
            _required.remove(req)
        if len(_required) not in (0, 4):
            raise MailValueError(f'MAIL: <missing min-config-parts : {_required}>')
        if not _required:
            if configurations.MAIL_FSC is None:
                configurations.MAIL_FSC = _buildpp(input('[MAIL_XF] Pepper\n|[ <IV=(0-999)><part=[+-]><prio=(1-9)>.<hops=(1-9)> ]| < ').strip())
            else:
                configurations.MAIL_FSC = _buildpp(configurations.MAIL_FSC)
            if configurations.MAIL_XFSEED is None:
                configurations.MAIL_XFSEED = pph("[MAIL_XF] Enter sha256 seed: ")
            if configurations.MAIL_RECEIVER_MAIL is None:
                configurations.MAIL_RECEIVER_MAIL = configurations.MAIL_SENDER_MAIL
            if configurations.MAIL_USER is None:
                configurations.MAIL_USER = configurations.MAIL_SENDER_MAIL
        return True
    return False


def run():

    if configurations.CONFIGURE_:
        _mk_defaults()
        _buildpp(configurations.BASIC_FSC_PEPPER)
        _build_attr()
        _read_ifhomerc()
        _read_ifurc()

    elif configurations.LATERAL_:
        _mk_defaults()
        _read_ifhomerc()
        _read_ifurc()
        _build_attr()

    elif configurations.HOST_SIDE:
        _mk_defaults()
        _read_ifhomerc()
        _read_ifurc()
        _build_attr()
        _check_faccess()
        _build_clientd()
        _check_authaccess()
        _set_localipparsif()
        _mailalert_defif()

    elif configurations.CLIENT_SIDE:
        _mk_defaults()
        _read_ifhomerc()
        _read_ifurc()
        _build_attr()
        _check_faccess()
        _build_hostd()
        _check_authaccess()
        _set_localipparsif()


try:

    run()

except Exception as e:
    tb = e.__traceback__
    trace = [tb.tb_frame]
    while tb.tb_next:
        trace.append(tb.tb_next.tb_frame)
        tb = tb.tb_next
    print(f"|[ {type(e)} ]|[ {e} ]".join(["\n|[ %s ]|" % t for t in trace]), file=stderr)
    configurations.EXP_EXIT(1)
