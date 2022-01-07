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

from typing import Literal, TextIO
from sys import argv, platform
from re import compile, search
from os import path, access, environ
from getpass import getpass
from ast import literal_eval
from subprocess import Popen, PIPE, TimeoutExpired

from sec.fscIO import pph
from sec.fscModule import FStreamCipher
from sec.vTools import mk_login
from config_interface._rc._run import attr_info_rev_file, gui_info_file
from config_interface.sec.doc_reader import get_all_keys, gen_infolines, get_sheet_json
from sec.fTools import print_cli_format
from _rc import configurations as CNF, _run
from sec.fTools import DefIfEndIf, LineFinder
from config_interface import msg_strings, ROOT_DIR


KEY_PATTERN = "PATTERN"
KEY_DEFAULT = "DEFAULT"
KEY_VALUE = "VALUE"
KEY_CAST = "CAST"
KEY_LIEV = "LIEV"

KW_PATTERN_S = {KEY_PATTERN: compile("\S+")}
KW_PATTERN_GT9 = {KEY_PATTERN: compile("^[1-9]\d+$")}
KW_PATTERN_FSC = {KEY_PATTERN: compile("^[1-9]\d{0,2}[+-][1-9]\.[1-9]$")}
KW_PATTERN_XFF = {KEY_PATTERN: compile("%s[^/\\\]*$")}
KW_CAST_INT = {KEY_CAST: int}
KW_CAST_PATH = {KEY_CAST: path.realpath}
KW_CAST_COD = {KEY_CAST: lambda c: c.encode(c).decode(c)}

#KW_LIEV_NONE = {KEY_LIEV: lambda _s: {"none": None}[_s.lower()]}
#KW_LIEV_BOOL = {KEY_LIEV: lambda _s: {"false": False, "true": True}[_s.lower()]}
#KW_LIEV_BOOLNONE = {KEY_LIEV: lambda _s: {"false": False, "true": True, "none": None}[_s.lower()]}

_KW_BASE = {
    KEY_PATTERN: compile("."),
    KEY_VALUE: None,
    KEY_CAST: str
}


def __getattr(attr: str): return getattr(CNF, attr.replace('* ', ''))


def __setattr(item: tuple): return setattr(CNF, item[0].replace('* ', ''), item[1][KEY_VALUE])


def __get_conf_item(attr, val='<None>'): return attr, {KEY_VALUE: (__getattr(attr) if val == '<None>' else val)}


def __setdefault_attr(item: tuple):
    if __getattr(item[0]) is None:
        __setattr(item)


def __setconf(config: dict):
    for item in config.items():
        __setattr(item)


def __setdefault_conf(config: dict):
    for item in config.items():
        __setdefault_attr(item)


def __replace42(attr: str) -> str: return attr.replace('* ', '')


def __add42(attr: str) -> str: return "* %s" % attr


def __fsc_tuple_to_str(_ttuple: tuple[int, tuple[int, int], int]) -> str:
    return "%d%s%d.%d" % (
        _ttuple[0], {0: '-', 1: '+'}[_ttuple[1][0]], _ttuple[1][1], _ttuple[2]
    )


CONFIG_LINE_FORM = "%-22s= %s"
def __config_file_ln_format(item: tuple) -> str:
    value = item[1][KEY_VALUE]
    if isinstance(value, str):
        value = f"{value!r}"
    return CONFIG_LINE_FORM % (__replace42(item[0]), value)

def _write_config_ln(io: TextIO, item: tuple):
    io.write(__config_file_ln_format(item) + '\n')

TRUE_PATTERNS = ("y", "Y", "yes", "Yes", "1", "ok")
YESNO_PATTERNS = "^(y|n|Y|N|yes|no|Yes|No|1|0|ok|x%s)$"
def __yesno(question: str,
            default: Literal["y", "n", "Y", "N", "yes", "no", "Yes", "No", "1", "0", "ok", "x"] = "yes",
            alternate: str = None,
            alternate_default: bool = False) -> [bool, None]:

    if alternate:
        pattern = compile(YESNO_PATTERNS % "|" + alternate)
        if alternate_default:
            default = alternate
    else:
        pattern = compile(YESNO_PATTERNS % "")

    def value() -> [bool, None]:
        if i in TRUE_PATTERNS:
            return True
        elif i == alternate:
            return None
        return False

    print(question, end="")
    while not search(pattern, (i := input("[%s]: " % default).strip())):
        if not i and default:
            i = default
            return value()
        print("!<Wrong Pattern> : Pattern=%s" % pattern.pattern)
        print(question, end="")
    return value()


def __value_input(attr: str, config: dict):
    default = config.get(KEY_DEFAULT)
    pattern = config.get(KEY_PATTERN)
    cast = config.get(KEY_CAST)
    liev = config.get(KEY_LIEV)

    def value():
        i = input("%s[%s]: " % (attr, default)).strip()

        if attr.startswith('* ') and (not i and default is None):
            if not search(pattern, str(i)):
                return print("!<Wrong Pattern> : Pattern=%s" % pattern.pattern)

        if not i:
            try:
                _default = config[KEY_DEFAULT]
                if isinstance(_default, (bool, tuple, list, set)):
                    config[KEY_VALUE] = _default
                else:
                    config[KEY_VALUE] = cast(_default)
            except KeyError:
                config[KEY_VALUE] = None
            return True

        if liev:
            try:
                config[KEY_VALUE] = liev(str(i))
                return True
            except KeyError:
                pass

        if search(pattern, str(i)):
            config[KEY_VALUE] = cast(str(i))
            return True
        else:
            return print("!<Wrong Pattern> : Pattern=%s" % pattern.pattern)

    if attr.startswith('* '):
        while not value():
            pass
    else:
        value()


def _value_interface(configs: dict[str, dict]):
    for attr in configs.copy():
        configs[attr] = (_KW_BASE | configs[attr]).copy()
        if __getattr(attr):
            configs[attr].setdefault(KEY_DEFAULT, __getattr(attr))
        __value_input(attr, configs[attr])
        configs[__replace42(attr)] = configs.pop(attr)


def _save_configs(configs: dict, _suffix: str = ""):
    _configs = configs.copy()
    if RC_FILE_LV1:
        line_finder = LineFinder(RC_FILE_LV1, configs)
        if line_finder.present_lines:
            print(msg_strings.SEPARATOR64)
            line_finder.print_present()
            print(msg_strings.SEPARATOR64)
            if __yesno(msg_strings.Q_OVERWRITE % f"{RC_FILE_LV1=}"):
                for m in line_finder.present_lines:
                    if _configs.get(m[2]):
                        line = __config_file_ln_format((m[2], _configs[m[2]]))
                        _configs.pop(m[2])
                    else:
                        line = ""
                    line_finder.overwrite_line_(m[0], line)
                for item in _configs.items():
                    line_finder.insert_remaining(__config_file_ln_format(item))
                line_finder.write_out()
                return print(msg_strings.FILE_CREATED % RC_FILE_LV1)

    _file = "%s.config%s.txt" % (CNF.USER, _suffix)

    with open(_file, "w") as file:
        file.write(msg_strings.SEPARATOR64 + "\n")
        for item in configs.items():
            _write_config_ln(file, item)
        file.write(msg_strings.SEPARATOR64 + "\n")
    print(msg_strings.FILE_CREATED % _file)


def _print_config(configs: dict):
    print(msg_strings.SEPARATOR64)
    for item in configs.items():
        print(__config_file_ln_format(item))
    print(msg_strings.SEPARATOR64)


def _mail_server_config() -> dict:
    configs = {
        __add42('MAIL_SMTP_ADDR'): KW_PATTERN_S,
        __add42('MAIL_SMTP_PORT'): KW_PATTERN_GT9 | KW_CAST_INT,
        __add42('MAIL_CRYPT'): {KEY_PATTERN: compile("^(ssl|SSL|tls|TLS)$")},
        __add42('MAIL_SENDER_MAIL'): KW_PATTERN_S,
        'MAIL_USER': KW_PATTERN_S,
        'MAIL_RECEIVER_MAIL': KW_PATTERN_S,
        'MAIL_BCC': KW_PATTERN_S
    }
    _value_interface(configs)
    return configs


def _mail_keyfile() -> dict:
    configs = {
        __add42('MAIL_FSC'): KW_PATTERN_FSC | {KEY_CAST: _run._parsbpp,
                                               KEY_DEFAULT: __fsc_tuple_to_str(CNF.BASIC_FSC_PEPPER)},
        __add42('MAIL_XF'): KW_PATTERN_XFF | KW_CAST_PATH
    }
    _value_interface(configs)
    configs |= {
        'MAIL_XFSEED': {KEY_VALUE: pph('! MAIL_XFSEED[None]: ')}
    }
    with open(configs['MAIL_XF'][KEY_VALUE] % CNF.USER, "wb") as f:
        f.write(
            FStreamCipher(
                getpass('! MAIL_ACCOUNT_PASSWORD[None]: ').encode(CNF.LOC_ENC),
                configs['MAIL_XFSEED'][KEY_VALUE],
                *configs['MAIL_FSC'][KEY_VALUE]
            ).encrypt())
    print(msg_strings.FILE_CREATED % configs['MAIL_XF'][KEY_VALUE] % CNF.USER)
    return configs


def _mail_test(config: dict = None):
    from _rc import configurations as CNF
    CNF.HOST_SIDE = True
    from _rc import _run
    if config:
        __setconf(config)
    else:
        config = {}
    try:
        _run.run()
        if _run.configurations.MAIL_CRYPT not in ('ssl', 'tls', 'SSL', 'TLS'):
            raise _run.MailValueError(ValueError())
    except _run.MailValueError:
        config = _mail_server_config()
        __setconf(config)
        _run.run()
    if not _run._mailalert_defif():
        config |= _mail_keyfile()
        __setconf(config)
    from _rc import _OBJrc
    hasattr(_OBJrc, "__file__")
    from sec.Loggers import MailAlert
    try:
        MailAlert().write(msg_strings.MAIL_ALERT_TEST + f"<{__file__}>\n\nEOF")
    except Exception as e:
        if type(e) in msg_strings.MAIL_EXCEPTION:
            print(msg_strings.MAIL_EXCEPTION[type(e)])
        else:
            print(msg_strings.MAIL_EXCEPTION[None])


def make_mail_alert(server_config: bool = True, key_file: bool = True):
    configs = dict()
    if server_config:
        configs |= _mail_server_config()
    if key_file:
        configs |= _mail_keyfile()
    if configs:
        _print_config(configs)
        if __yesno(msg_strings.Q_SAVE):
            _save_configs(configs, "-MailAlert")
    if __yesno(msg_strings.Q_TEST_MAIL, "No"):
        _mail_test(configs)


def _save_userline(userline: str):
    BOARD_USERS = CNF.BOARD_USERS
    defif = DefIfEndIf(BOARD_USERS, *CNF.IFDEFENDIF['BOARD_USERS'])
    if defif.configured:
        if (line_finder := LineFinder(BOARD_USERS, (CNF.USER,))).present_lines:
            print(msg_strings.SEPARATOR64)
            line_finder.print_present()
            print(msg_strings.SEPARATOR64)
            if __yesno(msg_strings.Q_OVERWRITE % f"{BOARD_USERS=}"):
                line_finder.final_insert(userline).write_out()
            else:
                line_finder.insert_after(userline).write_out()
            return print(msg_strings.FILE_CREATED % BOARD_USERS)
        LineFinder(BOARD_USERS, (CNF.IFDEFENDIF['BOARD_USERS'][1].decode(),)).insert_before(userline).write_out()
        return print(msg_strings.FILE_CREATED % BOARD_USERS)

    with open(BOARD_USERS, "wb") as f:
        f.write(
            b'\n%s\n%s\n%s' % (CNF.IFDEFENDIF['BOARD_USERS'][0], userline.encode(), CNF.IFDEFENDIF['BOARD_USERS'][1])
        )

    print(msg_strings.FILE_CREATED % BOARD_USERS)


def _login_files_config() -> dict:
    configs = {
        __add42('LOC_ENC'): KW_CAST_COD,
        __add42('FSC_HOST_SPICE_FILE'): KW_PATTERN_XFF | KW_CAST_PATH,
        __add42('FSC_HOST_XF'): KW_PATTERN_XFF | KW_CAST_PATH,
        __add42('FSC_HOST_TABLE_FILE'): KW_PATTERN_XFF | KW_CAST_PATH,
        __add42('FSC_PEPPER_HOST'): KW_PATTERN_XFF | KW_CAST_PATH,
        __add42('BASIC_FSC_PEPPER'): KW_PATTERN_FSC | {
            KEY_CAST: _run._parsbpp, KEY_DEFAULT: __fsc_tuple_to_str(CNF.BASIC_FSC_PEPPER)
        }
    }
    _value_interface(configs)
    return configs


def _login(configs: dict = None):
    _authkey_attr = {
        'lin': 'FSC_HOST_XF',
        'hst': 'FSC_HOST_TABLE_FILE',
        'spc': 'FSC_HOST_SPICE_FILE',
        'ppp': 'FSC_PEPPER_HOST',
        'bpp': 'BASIC_FSC_PEPPER'
    }
    bpp = 'bpp'
    if configs:
        CNF.AUTH_CONF = {CNF.USER: {item[0]: configs[item[1]][KEY_VALUE] % CNF.USER for item in _authkey_attr.items()
                                    if item[0] != bpp}}
        CNF.AUTH_CONF[CNF.USER][bpp] = configs[_authkey_attr[bpp]][KEY_VALUE]
        __setattr(('LOC_ENC', configs['LOC_ENC']))
    else:
        CNF.AUTH_CONF = {CNF.USER: {item[0]: __getattr(item[1]) % CNF.USER for item in _authkey_attr.items()
                                    if item[0] != bpp}}
        CNF.AUTH_CONF[CNF.USER][bpp] = __getattr(_authkey_attr[bpp])
    mk_login(
        CNF.USER,
        pph('! PASSPHRASE[None]: ')
    )
    [print(msg_strings.FILE_CREATED % CNF.AUTH_CONF[CNF.USER][file]) for file in CNF.AUTH_CONF[CNF.USER]
     if file != bpp]


def make_login_files(file_config: bool = True, login: bool = True):
    configs = None
    if file_config:
        configs = _login_files_config()
        _print_config(configs)
        if __yesno(msg_strings.Q_SAVE, "No"):
            _save_configs(configs, "-Login")
    if login:
        _login(configs)
        BASIC_FSC_PEPPER = CNF.AUTH_CONF[CNF.USER]['bpp']
        userline = "%s       bpp:%s" % (CNF.USER, __fsc_tuple_to_str(BASIC_FSC_PEPPER))
        BOARD_USERS = CNF.BOARD_USERS
        BASIC_FSC_PEPPER = f"{BASIC_FSC_PEPPER=}"
        BOARD_USERS = f"{BOARD_USERS=}"
        print('\n\t', userline, '\n')
        print(msg_strings.TOADD_USERLINE % BOARD_USERS)
        if __yesno(msg_strings.Q_SAVE_USERLINE % BOARD_USERS, "No"):
            _save_userline(userline)
        print(msg_strings.SEPARATOR64)
        print(msg_strings.CLIENT_PEPPERS % BASIC_FSC_PEPPER)
        print(msg_strings.SEPARATOR64)
        print(msg_strings.PAIRING_INTR % (CNF.USER, CNF.USER))


def _openssl_cmd() -> tuple[str, int]:
    _cmd = 2
    if platform == "linux":
        cmd = False
        for path in environ["PATH"].split(':'):
            if access(path + "/openssl", 1):
                cmd = path + "/openssl"
                _cmd = 0
                break
        if not cmd:
            cmd = "/usr/bin/openssl"
            _cmd = 1
    else:
        cmd = "openssl"
    return cmd, _cmd


def _openssl_exec(cmd) -> int:
    _sp = Popen([cmd],
                shell=True,
                stdin=-1,
                stderr=PIPE,
                stdout=PIPE
                )
    try:
        stdo, stde = _sp.communicate(timeout=3)
    except TimeoutExpired:
        stdo, stde = b"\n", b""
    print(stdo.decode(), end="")
    print(stde.decode(), end="")
    print(f"\n+++ exit {_sp.returncode} +++\n\n")
    return _sp.returncode


def make_openssl():
    configs = {
        __add42('SSL_CERT_FILE'): KW_CAST_PATH,
        __add42('SSL_KEY_FILE'): KW_CAST_PATH
    }
    _value_interface(configs)
    _cnf = "%s/%s" % (ROOT_DIR, "_rc/doc/openssl.cnf")
    if not (cnf := input('* openssl.cnf[%s]: ' % _cnf)):
        cnf = _cnf
    cnf = path.realpath(cnf)
    passwd = msg_strings.SSL_NODES
    if __yesno(msg_strings.Q_SSL_ENCRYP, "No"):
        configs |= {'SSL_PASSWORD': {KEY_VALUE: pph("! PASSPHRASE[None]: ")}}
        passwd = msg_strings.SSL_PASS_OUT % configs['SSL_PASSWORD'][KEY_VALUE]
    _print_config(configs)
    if __yesno(msg_strings.Q_SAVE, "No"):
        _save_configs(configs, "-ssl")
    cmd = _openssl_cmd()
    openssl_cmd = msg_strings.SSL_CMDLN % (
        cmd[0], configs['SSL_CERT_FILE'][KEY_VALUE], configs['SSL_KEY_FILE'][KEY_VALUE],
        cnf, passwd
    )
    if (msg := msg_strings.ERR_SSL.get(cmd[1])) is not None:
        print(msg)

    print(msg_strings.SEPARATOR64)
    print(openssl_cmd)
    print(msg_strings.SEPARATOR64)

    if msg is None and __yesno(msg_strings.Q_EXEC):
        rval = _openssl_exec(openssl_cmd)
        if rval == 0:
            if __yesno(msg_strings.Q_SSL_LOOKUP, "No"):
                print(msg_strings.SEPARATOR64)
                _openssl_exec(msg_strings.SSL_LOOKUP % (cmd[0], configs['SSL_CERT_FILE'][KEY_VALUE]))
        else:
            print(msg_strings.SEPARATOR64)
            print(msg_strings.ERR_SSL.get(4))


def man_pages(attr: str = None, index: bool = False):
    pages = get_all_keys(attr_info_rev_file)

    def _print_index():
        print_cli_format(pages, True, ": ", 6, lazy_columns=False)
        print(CNF.PCONT)
        CNF.PCONT = "\n"

    def _print_page(_attr):
        page = list(gen_infolines(_attr))
        for z in range(0, len(page)):
            print(page[~z], end="")

    if not attr and not index:
        _print_index()
        prompt = "man>"
        while True:
            i = input(prompt).strip()
            if search("^\d+$", str(i)):
                if (i := int(i) - 1) in range(len(pages)):
                    _print_page(pages[i])
            elif (attr := i) in pages:
                _print_page(attr)
            elif (attr := i.upper()) in pages:
                _print_page(attr)
            else:
                _print_index()
    elif index:
        _print_index()

    elif attr:
        if search("^\d+$", str(attr)) and (i := int(attr) - 1) in range(len(pages)):
            _print_page(pages[i])
        elif attr in pages:
            _print_page(attr)
        elif (attr := attr.upper()) in pages:
            _print_page(attr)
        else:
            raise ValueError


def make_sheet(defaults: bool = False, runc: str = False):
    configs = get_sheet_json(CNF.__file__)
    if runc:
        __setattr(__get_conf_item(runc, True))
        _run.run()
    elif defaults:
        _run._mk_defaults()

    _file = "%s.config-sheet.txt" % CNF.USER

    def getitem():
        val = __getattr(attr)
        try:
            if isinstance(val, str):
                _val = f"{val!r}"
            else:
                _val = f"{val}"
            literal_eval(_val)
        except SyntaxError as e:
            val = None
            print(msg_strings.ERR_CORRESPONDING_VAL % (attr, e.text))
        return __get_conf_item(attr, val)

    with open(_file, "w") as file:
        for unit in configs:
            file.write("\n# [ %s ]\n" % unit)
            for attr in configs[unit]:
                _write_config_ln(file, getitem())

    print(msg_strings.FILE_CREATED % _file)


def manual(page: str = None):
    if page in ('SefiTrash', '!'):
        return print(str().join(gen_infolines('SefiTrash', gui_info_file)))
    return print((page if (page := msg_strings.MANUALS.get(page)) else msg_strings.MANUALS.get(page)))


def main():

    def __base_config():
        global RC_FILE_LV1
        CNF.CONFIGURE_ = True
        _run.run()
        base_config = {
            '* USER': {KEY_DEFAULT: CNF.DEFAULT_USER},
            'RC_FILE_LV1': KW_CAST_PATH | {KEY_DEFAULT: False}
        }
        _value_interface(base_config)
        RC_FILE_LV1 = base_config['RC_FILE_LV1'][KEY_VALUE]
        __setconf(base_config)
        if CNF.RC_FILE_LV1 and not access(CNF.RC_FILE_LV1, 4):
            print(msg_strings.ERR_FILE_NOT_FOUND % CNF.RC_FILE_LV1)
            RC_FILE_LV1 = False
        _run.run()

    args = argv[1:]

    def man(_id: str):
        index = "index"
        if not args:
            return man_pages()
        if args[0] == index:
            return man_pages(index=True)
        try:
            return man_pages(attr=args[0])
        except ValueError:
            return manual(_id)

    def login(_id: str):
        login_only = "login"
        files = "files"
        __base_config()
        if not args:
            return make_login_files()
        if args[0] == login_only:
            return make_login_files(file_config=False)
        if args[0] == files:
            return make_login_files(login=False)
        return manual(_id)

    def mail(_id: str):
        server = "server"
        key = "key"
        test = "test"
        __base_config()
        if not args:
            return make_mail_alert()
        if args[0] == server:
            return make_mail_alert(key_file=False)
        if args[0] == key:
            return make_mail_alert(server_config=False)
        if args[0] == test:
            return _mail_test()
        return manual(_id)

    def sheet(_id: str):
        defaults = "defaults"
        runc = {
        'host': "HOST_SIDE",
        'client': "CLIENT_SIDE",
        'lateral': "LATERAL_"
        }
        if not args:
            return make_sheet()
        if args[0] == defaults:
            return make_sheet(defaults=True)
        if runc := runc.get(args[0]):
            __base_config()
            return make_sheet(runc=runc)
        return manual(_id)

    def ssl(_id: str):
        __base_config()
        return make_openssl()

    commands = {
        'man': man,
        'login': login,
        'mail': mail,
        'sheet': sheet,
        'ssl': ssl,
        'help': manual,
        None: manual
    }

    def _call(command):
        if command.endswith("?") and command[:-1] in commands:
            return commands.get(None).__call__(command[:-1])
        if args and args[0] in ("help", "-h", "-help", "--help", "?"):
            return commands.get(None).__call__(command)
        if command not in commands:
            return commands.get(None).__call__(command)
        return commands.get(command).__call__(command)
    try:
        try:
            _call(args.pop(0))
        except IndexError:
            prompt = "StCnfCli>"
            while (i := input(prompt).strip()) not in ("exit", "x", "0", "leave"):
                args = i.split()
                try:
                    _call(args.pop(0))
                except IndexError:
                    manual()
                except KeyboardInterrupt:
                    print()
                except EOFError as e:
                    raise e
                except Exception as e:
                    print("%s %s" % (type(e), e))
    except (KeyboardInterrupt, EOFError):
        exit('')
