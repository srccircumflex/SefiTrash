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


from os import get_terminal_size, scandir, access
from time import localtime, strftime, gmtime
from ast import literal_eval
from re import search, sub, escape, compile, Match
from pprint import pprint
from socket import socket, AF_INET, SOCK_DGRAM
from sys import getfilesystemencoding
from typing import Iterable

from _rc import configurations as CNF


class DefIfEndIf:
    def __init__(self, file, ifdef:bytes, endif:bytes, comnt:bytes):
        self.ifdef = ifdef.replace(b' ', b'')
        self.endif = endif.replace(b' ', b'')
        ifdef = b'\n' + self.ifdef
        endif = b'\n' + self.endif
        self.comnt = comnt
        self.file = file
        self.configured: bool = False
        try:
            with open(file, "rb") as f:
                file = f.read().replace(b' ', b'')
                if search(b"(\A|\n)" + self.ifdef, file) and not search(b"\n" + self.endif, file):
                    raise SyntaxError(rf"etc:{self.file} <{ifdef} without {endif}>")
                if search(b"\n" + self.endif, file) and not search(b"(\A|\n)" + self.ifdef, file):
                    raise SyntaxError(rf"etc:{self.file} <{endif} without {ifdef}>")
                if search(b"(\A|\n)" + self.ifdef, file) and search(b"\n" + self.endif, file):
                    self.configured = True
        except FileNotFoundError:
            pass

    def read_rc(self):
        assert self.configured, 'read_rc: read on UnDefinition'
        ifdef = False
        with open(self.file, "rb") as f:
            while True:
                ln = f.readline()
                if ln == b'\n': continue
                _ln = ln.replace(b' ', b'')
                if not ifdef and not (ifdef := _ln.startswith(self.ifdef)): continue
                if _ln.startswith(self.endif): return
                if _ln.startswith(self.comnt): continue
                yield ln

    def insert_rc(self):
        assert self.configured, 'insert_rc: insert at UnDefinition'
        ifdef = False
        pre_lines = b''
        with open(self.file, "rb") as f:
            while True:
                ln = f.readline()
                if ln == b'\n':
                    pre_lines += ln
                    continue
                _ln = ln.replace(b' ', b'')
                if not ifdef and not (ifdef := _ln.startswith(self.ifdef)):
                    pre_lines += ln
                    continue
                pre_lines += ln
                break
            while not (ln := f.readline()).replace(b' ', b'').startswith(self.endif):
                pass
            end_lines = ln + f.read()
        with open(self.file, "wb") as f:
            f.write(pre_lines)
            while True:
                ln: bytes = yield
                if ln is None:
                    f.write(end_lines)
                    return
                f.write(ln.strip() + b'\n')

    def insert_rc_all_(self, *args, encoding=getfilesystemencoding()):
        insert_rc = self.insert_rc()
        next(insert_rc)
        for ln in args:
            if not isinstance(ln, bytes):
                ln = ln.encode(encoding)
            insert_rc.send(ln)
        try:
            insert_rc.send(None)
        except StopIteration:
            pass


class LineFinder:
    def __init__(self, file: str, attrs: Iterable):
        self._last_index = 0
        self.present_lines: list[tuple[int, Match, str]] = list()
        self.file = file
        with open(file) as file:
            file = "\n" + file.read()
            self.lines = file.splitlines(True)
        for n, line in enumerate(self.lines):
            for _attr in attrs:
                if m := search("^" + _attr + "(\W.*|$)", line):
                    a = search("\w+", m.group()).group()
                    self.present_lines.append((n, m, a))

    def overwrite_line_(self, n: int, ln: str):
        self.lines[n] = ln + ("\n" if ln else "")
        if n > self._last_index:
            self._last_index = n
        return self

    def insert_remaining(self, ln: str):
        self.lines.insert(self._last_index, ln + "\n")
        return self

    def insert_before(self, ln: str):
        self.lines.insert(self.present_lines[0][0], ln + "\n")
        return self

    def insert_after(self, ln: str):
        self.lines.insert(self.present_lines[-1][0] + 1, ln + "\n")
        return self

    def write_out(self):
        with open(self.file, "w") as f:
            f.write(str().join(self.lines).strip())
        return self

    def flush(self):
        for m in self.present_lines:
            self.overwrite_line_(m[0], "")
        return self

    def final_insert(self, ln):
        if self.present_lines:
            self.overwrite_line_(self.present_lines.pop(0)[0], ln)
        else:
            self.insert_remaining(ln)
        self.flush()
        return self

    def print_present(self):
        for m in self.present_lines:
            print(m[1].group())
        return self


class ConsoleParser:

    def __init__(self, CMD_CONFIG: dict, intercept_options: dict, look_up: str=None):
        self.CMD_CONFIG: dict = CMD_CONFIG
        self.intercept_options: dict = intercept_options
        self._interception: [str, False] = False
        self.look_up: str = look_up

        self.command: str = None
        self.cmd_line: str = None
        self.cmd_split: list = None

        self.selected_opts_args: dict = None
        self.parsed_opts_args: tuple[dict, dict] = None

        self.config_item: tuple = None
        self.default: [None, str] = None
        self.func = None

    def splitter(self, cut_fun: bool = True) -> list:
        self.cmd_split = []
        if cut_fun:
            _cmd_line = sub("^\S+(\s+|$)", '', self.cmd_line)
        else:
            _cmd_line = self.cmd_line
        mask = False
        while _cmd_line:
            if m := search("^[^ ]*\\\\ ", _cmd_line):
                g = m.group()[:-2]
                if mask:
                    self.cmd_split[-1] += ' ' + g
                else:
                    self.cmd_split.append(g)
                mask = True
                _cmd_line = sub(m.re.pattern, '', _cmd_line, 1).strip()
            else:
                m = search("^[^ ]+", _cmd_line)
                g = m.group()
                if mask:
                    self.cmd_split[-1] += ' ' + g
                else:
                    self.cmd_split.append(g)
                mask = False
                _cmd_line = sub(m.re.pattern, '', _cmd_line, 1).strip()
        return self.cmd_split

    def _search_intercept(self, selected_opt: str):
        if selected_opt.startswith('--'):
            if selected_opt in self.intercept_options:
                self._interception = selected_opt
        else:
            for intercept_re in self.intercept_options:
                if not intercept_re.startswith('--') and search(f"^-{intercept_re}$", selected_opt):
                    self._interception = intercept_re
        return self._interception

    def pars_opts_args(self) -> dict:
        self.selected_opts_args = {"": []}
        current_opt = ""
        for n, part in enumerate(self.cmd_split):
            if part.startswith('-'):
                self._search_intercept(part)
                self.selected_opts_args.setdefault(part, list())
                current_opt = part
            else:
                self.selected_opts_args[current_opt].append(part)
        return self.selected_opts_args

    def get_verify_args(self, _key_config: [str, None], _key_selected: [str, None]) -> list:

        def mod2():
            if _key_selected:
                arg_re = compile(f"(?<=\s{_key_selected}\s).*")
            else:
                arg_re = compile(f"(?<={self.command}\s).*")
            cmd_line = self.cmd_line
            for consumed in arg_list:
                cmd_line = sub(sub(" ", "\\ ", escape(consumed)), "", cmd_line, 1)
            return search(arg_re, cmd_line).group().strip()

        z_args = self.config_item[1][_key_config]
        args = self.selected_opts_args[_key_selected]
        arg_list = []
        __key_selected = (_key_selected if _key_selected is not None else self.command)
        if isinstance(z_args, int):
            z_args = (z_args,)
        for n, mod in enumerate(z_args):
            if mod == 0:
                if len(args) != 0:
                    raise ValueError(f"{__key_selected} takes no arguments")
            if mod == 1:
                try:
                    arg_list.append(args[n])
                except IndexError:
                    raise ValueError(f"{__key_selected} : argument missing at position {n + 1}")
            if mod == 2:
                try:
                    if not (arg := mod2()):
                        raise AttributeError
                except AttributeError:
                    raise ValueError(f"{__key_selected} takes arguments")
                arg_list.append(arg)
            if mod == -1:
                try:
                    arg_list.append(args[n])
                except IndexError:
                    pass
            if mod == -2:
                try:
                    if arg := mod2():
                        arg_list.append(arg)
                except AttributeError:
                    pass
        return arg_list

    def get_verify_opts_args(self) -> tuple[dict, dict]:
        self.parsed_opts_args = ({'':[]},{'':[]})
        if isinstance(self.config_item[0], int):
            z_opts = range(self.config_item[0], self.config_item[0] + 1)
        else:
            z_opts = range(self.config_item[0][0], self.config_item[0][1] + 1)
        count = 0
        opt_keys = []
        default_args = {self.default: self.selected_opts_args.pop("")}

        for selected_opt in self.selected_opts_args:
            match = False
            for opt_conf in self.config_item[1]:
                if opt_conf is None:
                    continue
                if opt_conf.startswith('--') and selected_opt == opt_conf:
                    count += 1
                    match = True
                    break
                elif m := search(f"^-{opt_conf}$", selected_opt):
                    count += len(m.group()) - 1
                    match = True
                    break
            if not match:
                raise SyntaxError(f"unknown option {selected_opt}")
            opt_keys.append(opt_conf)

        if not opt_keys and None in self.config_item[1]:
            self.selected_opts_args[None] = default_args[None]
            args = self.get_verify_args(None, None)
            self.parsed_opts_args = {None: args}, {None: args}
            return self.parsed_opts_args

        if count not in z_opts:
            if self.default is not None:
                for opt_key in self.config_item[1]:
                    if opt_key.startswith('--'):
                        if opt_key == self.default:
                            default_key = opt_key
                            break
                    elif search(opt_key, self.default):
                        default_key = opt_key
                        break
                self.cmd_line = sub(f"^{self.command}", f"{self.command} {self.default} ", self.cmd_line)
                self.selected_opts_args = default_args
                try:
                    self._search_intercept(self.default)
                    args = self.get_verify_args(default_key, self.default)
                    if self.default.startswith('--'):
                        self.parsed_opts_args = {}, {self.default: args}
                        return self.parsed_opts_args
                    self.parsed_opts_args = {self.default: args}, {}
                    return self.parsed_opts_args
                except Exception as e:
                    if self._interception:
                        pass
                    else:
                        raise e
            raise SyntaxError(f"{self.command} : unexpected range of options")

        for key, opt in zip(opt_keys, self.selected_opts_args):
            self.selected_opts_args[opt] = self.get_verify_args(key, opt)

        self.parsed_opts_args = ({
                   item[0]: item[1] for item in self.selected_opts_args.items()
                   if not item[0].startswith('--')
               }, {
                   item[0]: item[1] for item in self.selected_opts_args.items()
                   if item[0].startswith('--')
               })
        return self.parsed_opts_args

    def _heed_interception(self):
        def intercept():
            item = self.intercept_options[self._interception]
            if isinstance(item, tuple):
                return item[0].__call__(**{item[1]: self})
            return item.__call__(self)

        if self._interception:
            try:
                self.get_verify_opts_args()
            except Exception:
                pass
            return intercept()

        _options = self.get_verify_opts_args()
        if self._interception:
            return intercept()
        return _options

    def pars_string(self, cmd_line: str) -> [None, tuple[dict, dict]]:
        if not cmd_line: return
        self.cmd_line = cmd_line.strip()
        self.command = cmd_line.split()[0]
        self._interception = False
        if self.command not in self.CMD_CONFIG:
            return self.print_look_up()

        self.func = self.CMD_CONFIG[self.command][0]
        self.config_item = list(self.CMD_CONFIG[self.command][1].items())[0]

        if not (default := self.CMD_CONFIG[self.command][1].get(0)):
            self.default = self.CMD_CONFIG[self.command][1].get(None)
        else:
            self.default = default

        self.splitter()
        self.pars_opts_args()
        return self._heed_interception()

    def get_merged(self) -> tuple[tuple[str, list], list]:
        short = ""
        longs = []
        args = []
        if None in self.parsed_opts_args[0]:
            return ("", []), self.parsed_opts_args[0][None]
        for short_item in self.parsed_opts_args[0].items():
            short += short_item[0][1:]
            args.extend(short_item[1])
        for longs_item in self.parsed_opts_args[1].items():
            longs.append(longs_item[0][2:])
            args.extend(longs_item[1])
        if short or longs or args:
            return (short, longs), args

    def print_look_up(self):
        if not self.look_up:
            self.look_up = ""
            _look_line = ""
            for command in self.CMD_CONFIG:
                _look_line += "%-10s " % command
                if len(_look_line) > 40:
                    self.look_up += _look_line.strip() + '\n'
                    _look_line = ""
            if _look_line:
                self.look_up += _look_line
            self.look_up = self.look_up.strip()
        print(self.look_up)


def print_cli_format(content: list, enum: bool = False, enum_symbl: str = "", columns: int = 4,
                     central_headl: str = None, atentt: str = "", begin: str = "", end_hl: str = "\n",
                     lazy_columns: bool = False):
    try:
        terminal_colums = get_terminal_size()[0]
    except OSError as e:
        print(e)
        terminal_colums = 128
    q_terminal_colums, cnt = terminal_colums // columns, 0
    m_central_headl = f"{begin}{atentt} {central_headl} {atentt}"
    if central_headl and len(m_central_headl) <= columns * q_terminal_colums:
        CNF.PCONT += f"{' ' * ((columns * q_terminal_colums - len(m_central_headl)) // 2)}{m_central_headl}" + end_hl + '\n'
    elif central_headl:
        CNF.PCONT += begin + central_headl + end_hl + '\n'

    line = ""

    for n, cont in enumerate(content):
        _symbl = ("{:2}{}".format(n + 1, enum_symbl) if enum else enum_symbl)
        if cnt == columns: CNF.PCONT += line + '\n'; line = ""; cnt = 0
        cont = _symbl + cont + ' '
        while '\t' in cont:
            tap_p = cont.index('\t')
            cont = cont[:tap_p] + ' ' * (4 - (len(cont[:tap_p]) % 4)) + cont[tap_p + 1:]
        l_cont = len(cont)
        if l_cont >= terminal_colums:
            if line != "": CNF.PCONT += line + '\n'; line = ""; cnt = 0
            CNF.PCONT += cont + '\n'
            continue
        if l_cont <= q_terminal_colums:
            line += f"{cont}{' ' * (q_terminal_colums - l_cont)}"
            cnt += 1
            continue
        elif lazy_columns:
            if line != "": CNF.PCONT += line + '\n'; line = ""; cnt = 0
            CNF.PCONT += cont + '\n'
            continue
        if l_cont > q_terminal_colums * (columns - cnt): CNF.PCONT += line + '\n'; line = ""; cnt = 0
        for mulp in range(1, columns - cnt + 1):
            if l_cont <= q_terminal_colums * mulp:
                line += f"{cont}{' ' * (q_terminal_colums * mulp - l_cont)}"
                cnt += mulp
                break
    if line != "": CNF.PCONT += line + '\n'


def print_pwd(jsn: dict, _listing: bool = False):
    if _listing and 'user' in jsn:
        CNF.PCONT += "user: %(user)s\n---\n" % jsn
    if _listing and 'home' in jsn:
        CNF.PCONT += "home: %(home)s\n---\n" % jsn
    CNF.PCONT += "src: %(current)s\n" % jsn['src']
    if _listing:
        for _kw in jsn['src']:
            if _kw == 'current': continue
            CNF.PCONT += f" - {_kw}: {jsn['src'][_kw]}\n"
    CNF.PCONT += "dst: %(current)s\n" % jsn['dst']
    if _listing:
        for _kw in jsn['dst']:
            if _kw == 'current': continue
            CNF.PCONT += f" - {_kw}: {jsn['dst'][_kw]}\n"


class PpStr:
    def __init__(self): self.cont = ""

    def write(self, arg): self.cont += arg


def print_dir_listing(o__Dir, _all: bool = False):
    if _all:
        for file in (jsn := o__Dir.fformat()):
            CNF.PCONT += f"--> {file}:\n"
            ppstr = PpStr()
            pprint(jsn[file], stream=ppstr)
            CNF.PCONT += ppstr.cont
        return
    _headln = "_file_                           _mod-time_       _≈size_\n" \
              "========================================================="
    _format = "%(file)-32s %(st_mtime)s   %(size)s"
    CNF.PCONT += _headln + '\n'
    for file in (jsn := o__Dir.fformat()):
        _form = {'file': file, 'size': '?'}
        _form |= jsn[file]
        _consize = list(jsn[file]['st_size'])
        _consize.reverse()
        for _sz in _consize:
            if jsn[file]['st_size'][_sz]:
                _form['size'] = "%d%s" % (jsn[file]['st_size'][_sz], _sz)
                break
        CNF.PCONT += _format % _form + '\n'


class ConvertDirHeader:

    def __init__(self, header, time_format: str = None, utc: bool = False):

        self.formt = (time_format if time_format is not None else
                      CNF.DIR_TIME_FORM)
        self.utc = utc

        self.header = header
        self.stats_convert: dict = {
            'st_mode': self.stat_origin_result,
            'st_ino': self.stat_origin_result,
            'st_dev': self.stat_origin_result,
            'st_nlink': self.stat_origin_result,
            'st_uid': self.stat_origin_result,
            'st_gid': self.stat_origin_result,
            'st_size': self.stat_size_conv,
            'st_atime': self.stat_time_conv,
            'st_mtime': self.stat_time_conv,
            'st_ctime': self.stat_time_conv
        }

    @staticmethod
    def stat_origin_result(_stat) -> str:
        return str(_stat)

    def stat_time_conv(self, _stat) -> str:
        if self.utc:
            return strftime(self.formt, gmtime(_stat))
        return strftime(self.formt, localtime(_stat))

    @staticmethod
    def stat_size_conv(_stat) -> dict[str:int]:
        return {
            'B': _stat,
            'K': round(_stat / 1024),
            'M': round(_stat / 1024 / 1024),
            'G': round(_stat / 1024 / 1024 / 1024),
        }

    def _str(self):
        if type(self.header) == str: return self.header
        return self.header.decode(CNF.SRM_ENC, errors="replace")

    def _liev(self):
        if type(self.header) in (tuple, list, dict, set): return self.header
        return literal_eval(self._str())

    def fformat(self):
        h_convert: dict = self._liev()
        for file_header in h_convert:
            for header_content_type in h_convert[file_header]:
                h_convert[
                    file_header
                ][
                    header_content_type
                ] = self.stats_convert[
                    header_content_type
                ].__call__(
                    h_convert[
                        file_header
                    ][
                        header_content_type
                    ]
                )
        return h_convert


class DirHeaders:

    def __init__(self, path: str = None):

        self.dir_entrys: list = list()
        dir_entrys = scandir(path)
        while True:
            try:
                self.dir_entrys.append(next(dir_entrys))
            except StopIteration:
                break

    def mk_header(self) -> dict:
        headers: dict = dict()
        for entry in self.dir_entrys:
            if entry.is_dir() and access(entry.path, 5):
                headers.setdefault(entry.name + '/', dict())
            elif entry.is_file() and access(entry.path, 4):
                headers.setdefault(entry.name, dict())
            else:
                continue
            entry_stats = list(entry.stat())
            for st_i in CNF.DIR_STAT_TAGS:
                headers[list(headers)[-1]].setdefault(CNF.DIR_STAT_TAGS[st_i], entry_stats[st_i])
        return headers

    def liev_(self):
        return self.mk_header()

    def __str__(self):
        return str(self.liev_())

    def __bytes__(self):
        return self.__str__().encode(CNF.SRM_ENC, errors="replace")


def print_manualpage(cmd: str = 'help', parser: ConsoleParser = None):
    if parser:
        cmd = parser.command
    with open(CNF.MAIN_ROOT + '/_rc/.console.manual') as f:
        for _page in (_pages := f.read().split('#' * 90)):
            if _page.strip().startswith(cmd):
                CNF.PCONT += _page
                break


def exp_full_trace(exp: Exception) -> list:
    tb = exp.__traceback__
    trace = [tb.tb_frame]
    while tb.tb_next:
        trace.append(tb.tb_next.tb_frame)
        tb = tb.tb_next
    return trace


def getpublicip():
    from urllib.request import Request, urlopen
    return urlopen(Request("http://www.ifconfig.me")).read().decode('utf8')


def getlocalip(DNS:str="8.8.8.8"):
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.connect((DNS, 80))
            return s.getsockname()[0]
        finally:
            s.close()


def subwinpath(path: str):
    return sub(":/?", ":/", sub("\\\+", "/", path))

def subwininval(path: str):
    return sub('(?<!^\w)[\\\\:*?<>|"]', "_", path)
