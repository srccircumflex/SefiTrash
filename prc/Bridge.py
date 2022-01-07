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

from time import asctime, sleep
from queue import Queue
from _queue import Empty
from os import stat
from pprint import pprint
from ast import literal_eval
from re import search

from _rc import configurations as CNF

from sec.fscIO import pph
from sec.fTools import ConvertDirHeader, DirHeaders, print_cli_format, print_pwd, print_dir_listing
from sec.PermCTL import SecurePath
from sec.Proto import ModuleFormats, StreamHeader, PortFormats, resp, pf
from sec.Loggers import LOGS_

mf = ModuleFormats()

class Bridge:

    def __init__(self, pipe_in:Queue, pipe_out:Queue, client:dict):

        self.bridge_lock: bool = False
        self.bridge_solved: bool = True

        self.o__Dir: ConvertDirHeader = None
        self.o__Jsn: dict = None

        self.SECURE_PATH = SecurePath(client)
        self.client:dict = client
        self.pipe_in:Queue = pipe_in
        self.pipe_out:Queue = pipe_out
        self.header:StreamHeader = None

        self._pre_GET = resp.rRES(resp.CODEs.Processing)
        self._pre_PUT = resp.rRES(resp.CODEs.Processing)
        self._pre_PUF = resp.rRES(resp.CODEs.Processing)
        self._pre_CLS = resp.rRES(resp.CODEs.OK)

    def _do_RES(self) -> None:
        if self.header.option_list and self.header.option_list[0] == 1: self.bridge_solved = True
        if (resl := self.header.option_list) is None or resl[0] >= 200: self.bridge_lock = False
        LOGS_.bridge.logg(20, self.header.option)

    # //GET// {"m":<"[fFaAlL]">, "l1":<n>} ///
    # {"S":<src-path>, "D":<dst-path>}
    # ->
    # //PUT// {"m":"[fFaA]","l1":<l-dst-path>,"l2":<l-data>} ///  # ||
    # //RET// {"m":"[lL]","l1":<l-data>} ///
    def _do_GET(self) -> bytes:
        _qualname = self._do_GET.__qualname__
        try:
            paths = literal_eval(str().join(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC) for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"])))
            if self.header.option_liev['m'] in ('l', 'L'):
                src = self.SECURE_PATH.src_l_path(paths['S'])
                if src:
                    dir_scan = DirHeaders(src).__bytes__()
                    self.pipe_out.put(mf.RET_f % (self.header.option_liev['m'].encode(CNF.SRM_ENC), len(dir_scan)))
                    [self.pipe_out.put(dir_scan[b * CNF.DAT_READ_BUFFER:CNF.DAT_READ_BUFFER * (b + 1)]) for b in CNF.BUFFER_ITER(len(dir_scan), CNF.DAT_READ_BUFFER)]
                    return resp.rRES(resp.CODEs.OK)
                return resp.bEXP(resp.CODEs.NotFound, _qualname)
            elif self.header.option_liev['m'] in ('f', 'F', 'a', 'A'):
                src = self.SECURE_PATH.src_f_path(paths['S'])
                if src:
                    self.pipe_out.put(mf.PUT_f % (self.header.option_liev['m'].encode(CNF.SRM_ENC), len(paths["D"]), stat(src).st_size))
                    self.pipe_out.put(paths["D"].encode(CNF.SRM_ENC))
                    with open(src, "rb") as f: [self.pipe_out.put(f.read(CNF.DAT_READ_BUFFER)) for _ in CNF.BUFFER_ITER(stat(src).st_size, CNF.DAT_READ_BUFFER)]
                    return resp.rRES(resp.CODEs.OK)
                return resp.bEXP(resp.CODEs.NotFound, _qualname)
            raise AttributeError(f"{self.header.option_liev['m']=}")
        except Empty as e:
            return resp.bEXP(resp.CODEs.LengthRequired, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))

    # //PUT// {"m":"[fFaA]","l1":<l-dst-path>,"l2":<l-data>} ///
    def _do_PUT(self) -> bytes:
        _qualname = self._do_PUT.__qualname__
        try:
            if self.header.option_liev["m"] in ('f', 'F', 'a', 'A'):
                path = str().join(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC) for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"]))

                try:
                    if self.header.option_liev["m"] == "F": path = self.SECURE_PATH.dst_path(path)
                    elif self.header.option_liev["m"] == "f": path = self.SECURE_PATH.dst_secure_path(path)
                    elif self.header.option_liev["m"] == "A": path = self.SECURE_PATH.dst_a(path)
                    elif self.header.option_liev["m"] == "a": path = self.SECURE_PATH.dst_secure_a(path)
                except FileExistsError as e:
                    [self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT) for _ in CNF.BUFFER_ITER(self.header.option_liev["l2"])]
                    return resp.bEXP(resp.CODEs.Unauthorized, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))

                if path:
                    with open(path, "wb") as f: [f.write(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT)) for _ in CNF.BUFFER_ITER(self.header.option_liev["l2"])]
                    return resp.rRES(resp.CODEs.Created)
                [self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT) for _ in CNF.BUFFER_ITER(self.header.option_liev["l2"])]
                return resp.bEXP(resp.CODEs.NotFound, _qualname)
            raise AttributeError(f"{self.header.option_liev['m']=}")
        except Empty as e:
            return resp.bEXP(resp.CODEs.LengthRequired, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))

    # //LOG// {"m":<"[tj]">,"l1"<l-data>} ///
    def _do_LOG(self) -> bytes:
        _qualname = self._do_LOG.__qualname__
        try:
            if self.header.option_liev['m'] == "j":
                json_ = literal_eval(str().join(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC, errors="replace") for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"])))
                with open(CNF.LOG_REMOTE, 'a') as f:
                    f.write(f"[----{asctime()}----]\n")
                    for key in json_:
                        f.write(f"{key}:    {json_[key]} \t#EOL#\n")
                    f.write("\n-------------[EOLog]--------------\n")
                return resp.rRES(resp.CODEs.Created)
            if self.header.option_liev['m'] == "t":
                with open(CNF.LOG_REMOTE, 'a') as f:
                    f.write(f"[----{asctime()}----]\n")
                    for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"]):
                        f.write(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC, errors="replace"))
                    f.write("\n-------------[EOLog]--------------\n")
                return resp.rRES(resp.CODEs.Created)
            raise AttributeError(f"{self.header.option_liev['m']=}")
        except Empty as e:
            return resp.bEXP(resp.CODEs.LengthRequired, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))

    # //CHD// {"m": <"[sda]">, "l1": <len>} ///
    def _do_CHD(self) -> bytes:
        _qualname = self._do_CHD.__qualname__
        try:
            path = str().join(self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC) for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"]))
            if _attrl := {'d': ('dst',), 's': ('src',), 'a': ('src', 'dst')}.get(self.header.option_liev["m"]):
                for _prt in _attrl:
                    _attr = 'cd_' + _prt
                    if hasattr(self.SECURE_PATH, _attr):
                        if not getattr(self.SECURE_PATH, _attr).__call__(path):
                            return resp.rRES(resp.CODEs.Forbidden)
                    else: return resp.rRES(resp.CODEs.NotImplementError)
                return resp.rRES(resp.CODEs.Created)
            raise NotImplementedError
        except Empty as e:
            return resp.bEXP(resp.CODEs.LengthRequired, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))

    # //PWD// {"m": <"[pcua]">} ///
    def _do_PWD(self) -> bytes:
        _qualname = self._do_PWD.__qualname__
        try:
            if search("[apcu]{1,3}", self.header.option_liev['m']):
                ret = {'src': {'current': None},'dst': {'current': None}}
                if 'a' in self.header.option_liev['m']: self.header.option_liev['m'] = 'pcu'
                if 'p' in self.header.option_liev['m']:
                    ret['src'] |= {'current': self.SECURE_PATH.SRCDST['src']['current']}
                    ret['dst'] |= {'current': self.SECURE_PATH.SRCDST['dst']['current']}
                if 'c' in self.header.option_liev['m']:
                    ret['src'] |= {'black': self.SECURE_PATH.SRCDST['src']['black']}
                    ret['src'] |= {'white': self.SECURE_PATH.SRCDST['src']['white']}
                    ret['dst'] |= {'black': self.SECURE_PATH.SRCDST['dst']['black']}
                    ret['dst'] |= {'white': self.SECURE_PATH.SRCDST['dst']['white']}
                    ret['src'] |= {'root': self.SECURE_PATH.SRCDST['src']['root']}
                    ret['dst'] |= {'root': self.SECURE_PATH.SRCDST['dst']['root']}
                if 'u' in self.header.option_liev['m']:
                    ret |= {'user': CNF.USER}
                    ret |= {'home': CNF.HOME_PATH}
                ret = str(ret).encode(CNF.SRM_ENC)
                self.pipe_out.put(mf.RET_f % (b'p', len(ret)))
                [self.pipe_out.put(ret[b * CNF.DAT_READ_BUFFER:CNF.DAT_READ_BUFFER * (b + 1)]) for b in CNF.BUFFER_ITER(len(ret), CNF.DAT_READ_BUFFER)]
                return resp.rRES(resp.CODEs.OK)
            raise AttributeError(f"{self.header.option_liev['m']=}")
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))

    # //RET// {"m": <"[lpL]">} ///
    def _do_RET(self) -> bytes:
        _qualname = self._do_RET.__qualname__
        try:
            if self.header.option_liev["m"] in ('l', 'L'):
                data = str().join(
                    self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC) for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"]))
                self.o__Dir = ConvertDirHeader(data)
                if self.header.option_liev["m"] == "l": print_cli_format(self.o__Dir.fformat())
                return resp.rRES(resp.CODEs.Created)
            elif self.header.option_liev["m"] == "p":
                data = str().join(
                    self.pipe_in.get(timeout=CNF.QUEUE_TIMEOUT).decode(CNF.SRM_ENC) for _ in CNF.BUFFER_ITER(self.header.option_liev["l1"]))
                self.o__Jsn = literal_eval(data)
                print_pwd(self.o__Jsn)
                return resp.rRES(resp.CODEs.Created)
        except Empty as e:
            return resp.bEXP(resp.CODEs.LengthRequired, f"{_qualname} {type(e)} {e}".encode(CNF.LOC_ENC, errors="replace"))
        except Exception as e:
            tb = e.__traceback__
            trace = [tb.tb_frame]
            while tb.tb_next:
                trace.append(tb.tb_next.tb_frame)
                tb = tb.tb_next
            return resp.bEXP(resp.CODEs.BadRequest, f"{_qualname} {type(e)} {e} {trace}".encode(CNF.LOC_ENC, errors="replace"))


class BridgeFactory:

    default_dir_file = "dirlist.txt"

    def __init__(self, pipe_out:Queue, __oBRIDGE:Bridge):
        self.pipe_out = pipe_out
        self.BRIDGE = __oBRIDGE

    def mks_PWD(self, opts: tuple):

        if 'list' in opts[1] and self.BRIDGE.o__Jsn is not None:
            print_pwd(self.BRIDGE.o__Jsn, _listing=True)
            return
        elif 'L' in opts[0]:
            self.BRIDGE.o__Jsn = self.BRIDGE.SECURE_PATH.SRCDST
            print_pwd(self.BRIDGE.o__Jsn)
            return

        self.BRIDGE.bridge_lock = True
        if self.BRIDGE.header: self.BRIDGE.header.option_list = None

        self.pipe_out.put(mf.PWD_f % opts[0].encode(CNF.SRM_ENC))

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def _mks_RGET(self, mod, src, dst):

        __rr, __lm = ((True, b'L') if mod.lower() == 'rr' else (False, b'l'))
        dst, __rm = ((self.BRIDGE.SECURE_PATH.dst_secure_a(dst + '/#'), b'f') if 'r' in mod
                     else (self.BRIDGE.SECURE_PATH.dst_a(dst + '/#'), b'F'))
        if dst is False: raise FileNotFoundError

        self.BRIDGE.o__Dir = None
        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        _sub = mf.GET_sub % (src.encode(CNF.SRM_ENC), dst.encode(CNF.SRM_ENC))
        get = mf.GET_f % (__lm, len(_sub))

        self.pipe_out.put(get)
        self.pipe_out.put(_sub)

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock:
                if (resl := self.BRIDGE.header.option_list) and resl[0] not in range(200, 300):
                    print("l!- %d" % resl[0])
                break

        if not self.BRIDGE.o__Dir:
            LOGS_.bridge.logg(10, CNF.STRINGS.fe_TIMEOUT % (CNF.RESPONSE_TIMEOUT * CNF.RESPONSE_TIMEOUT_ADJUST), mt=self._mks_RGET)
            for _ in range(CNF.RESPONSE_TIMEOUT):
                sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
                if self.BRIDGE.o__Dir: break
        if not self.BRIDGE.o__Dir:
            LOGS_.bridge.logg(40, CNF.STRINGS.NOTGETTING % src, mt=self._mks_RGET, ansi=CNF.MSG_ANSI.red)
            return

        for f in self.BRIDGE.o__Dir.fformat():
            if f.endswith('/'):
                if __rr:
                    print('-l?: ' + src + '/' + f)
                    self._mks_RGET(mod, src + '/' + f, dst[:-1] + f)
                continue
            _sub = mf.GET_sub % ((src + '/' + f).encode(CNF.SRM_ENC), (dst[:-1] + f).encode(CNF.SRM_ENC))
            get = mf.GET_f % (__rm, len(_sub))
            self.pipe_out.put(get)
            self.pipe_out.put(_sub)

    def mks_GET(self, opts: tuple, src: str= "", dst: str= ""):

        if 'enum' in opts[1] and self.BRIDGE.o__Dir is not None:
            print_cli_format(self.BRIDGE.o__Dir.fformat(), enum=True, enum_symbl=' # ')
            return
        elif 'list' in opts[1] and self.BRIDGE.o__Dir is not None:
            print_dir_listing(self.BRIDGE.o__Dir)
            return
        elif 'List' in opts[1] and self.BRIDGE.o__Dir is not None:
            print_dir_listing(self.BRIDGE.o__Dir, _all=True)
            return
        elif 'tform' in opts[1] and self.BRIDGE.o__Dir is not None:
            self.BRIDGE.o__Dir.formt = src
            return
        elif 'tutc' in opts[1] and self.BRIDGE.o__Dir is not None:
            self.BRIDGE.o__Dir.utc = src
            return
        elif 'write' in opts[1] and self.BRIDGE.o__Dir is not None:
            with open((src if src else self.default_dir_file), "a") as f:
                pprint(self.BRIDGE.o__Dir.fformat(), stream=f)
                f.write('\n')
            return
        elif opts[1]: raise AttributeError(f"{opts[1]=}")

        mod = opts[0]

        if mod.startswith('n'):
            if self.BRIDGE.o__Dir: src = list(self.BRIDGE.o__Dir.fformat())[int(src) - 1]
            else: raise AttributeError
            mod = mod[1:]

        if mod == 'L':
            src = self.BRIDGE.SECURE_PATH.src_l_path(src)
            if not src: raise FileNotFoundError
            self.BRIDGE.o__Dir = ConvertDirHeader(DirHeaders(src).__bytes__())
            print_cli_format(self.BRIDGE.o__Dir.fformat())
            return

        if mod != 'l': dst = self.BRIDGE.SECURE_PATH.assifnodst(src, dst)

        if mod in ('r', 'rr', 'R', 'RR'):
            self.BRIDGE.bridge_solved = False
            try:
                self._mks_RGET(mod, src, dst)
            except KeyboardInterrupt:
                return print()
            finally:
                self.BRIDGE.o__Dir = None
            self.pipe_out.put(pf.bend % resp.rRES(b'1'))
            for _ in range(CNF.RESPONSE_TIMEOUT):
                sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
                if self.BRIDGE.bridge_solved: return
            for _ in range(CNF.RESPONSE_TIMEOUT):
                sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
                if self.BRIDGE.bridge_solved: return
            raise TimeoutError

        if mod == 'f': dst = self.BRIDGE.SECURE_PATH.dst_secure_path(dst)
        elif mod == 'F': dst = self.BRIDGE.SECURE_PATH.dst_path(dst)
        elif mod == 'a': dst = self.BRIDGE.SECURE_PATH.dst_secure_a(dst)
        elif mod == 'A': dst = self.BRIDGE.SECURE_PATH.dst_a(dst)
        elif mod != 'l': raise AttributeError(f"{opts=}")
        if dst is False: raise FileNotFoundError

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        _sub = mf.GET_sub % (src.encode(CNF.SRM_ENC), dst.encode(CNF.SRM_ENC))
        get = mf.GET_f % (mod.encode(CNF.SRM_ENC), len(_sub))
        self.pipe_out.put(get)
        self.pipe_out.put(_sub)

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def _mks_RPUT(self, mod, src, dst):

        __rr = (True if mod.lower() == 'rr' else False)
        __rm = (b'a' if 'r' in mod else b'A')

        src = self.BRIDGE.SECURE_PATH.src_l_path(src)
        if src is False: return
        o__Dir = ConvertDirHeader(DirHeaders(src).__bytes__())

        for f in o__Dir.fformat():
            if f.endswith('/'):
                if __rr: self._mks_RPUT(mod, src + '/' + f, dst + '/' + f)
                continue
            _src = self.BRIDGE.SECURE_PATH.src_f_path(src + '/' + f)
            if not _src: continue
            _dst = (dst + '/' + f).encode(CNF.SRM_ENC)
            put = mf.PUT_f % (__rm, len(_dst), stat(_src).st_size)
            self.pipe_out.put(put)
            self.pipe_out.put(_dst)
            with open(_src, "rb") as _f: [self.pipe_out.put(_f.read(CNF.DAT_READ_BUFFER)) for _ in CNF.BUFFER_ITER(stat(_src).st_size, CNF.DAT_READ_BUFFER)]

    def mks_PUT(self, opts: tuple, src: str, dst: str= ""):

        mod = opts[0]

        if mod.startswith('n'):
            if self.BRIDGE.o__Dir: src = list(self.BRIDGE.o__Dir.fformat())[int(src) - 1]
            else: raise AttributeError
            mod = mod[1:]

        src = self.BRIDGE.SECURE_PATH.src_f_path(src)
        if src is False: raise FileNotFoundError

        dst = self.BRIDGE.SECURE_PATH.rassifnodst(src, dst)

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        if mod in ('r', 'rr', 'R', 'RR'):
            self.BRIDGE.bridge_solved = False
            try:
                self._mks_RPUT(mod, src, dst)
            except KeyboardInterrupt:
                return print()
            self.pipe_out.put(pf.bend % resp.rRES(b'1'))
            for _ in range(CNF.RESPONSE_TIMEOUT):
                sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
                if self.BRIDGE.bridge_solved: return
            for _ in range(CNF.RESPONSE_TIMEOUT):
                sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
                if self.BRIDGE.bridge_solved: return
            raise TimeoutError

        dst = dst.encode(CNF.SRM_ENC)
        put = mf.PUT_f % (mod.encode(CNF.SRM_ENC), len(dst), stat(src).st_size)
        self.pipe_out.put(put)
        self.pipe_out.put(dst)
        with open(src, "rb") as f: [self.pipe_out.put(f.read(CNF.DAT_READ_BUFFER)) for _ in CNF.BUFFER_ITER(stat(src).st_size, CNF.DAT_READ_BUFFER)]

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def send_LOG(self, opts: tuple, dat: str):

        mod = opts[0]

        if mod == 'j': literal_eval(dat)

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        self.pipe_out.put(mf.LOG_f % (mod.encode(CNF.SRM_ENC), len(dat)))
        self.pipe_out.put(dat.encode(CNF.SRM_ENC))

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def mks_CHD(self, opts: tuple, dst: str):

        mod = opts[0]

        if _attrl := {'D': ('dst',), 'S': ('src',), 'A': ('src', 'dst')}.get(mod):
            for _prt in _attrl:
                _attr = 'cd_' + _prt
                if hasattr(self.BRIDGE.SECURE_PATH, _attr):
                    if not getattr(self.BRIDGE.SECURE_PATH, _attr).__call__(dst):
                        raise FileNotFoundError
                else: raise NotImplementedError(f"{_attr=}")
            return

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        self.pipe_out.put(mf.CHD_f % (mod.encode(CNF.SRM_ENC), len(dst)))
        self.pipe_out.put(dst.encode(CNF.SRM_ENC))

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break


class PortFactory(PortFormats):

    def __init__(self, pipe_out, __oBRIDGE):
        PortFormats.__init__(self)
        self.pipe_out = pipe_out
        self.BRIDGE = __oBRIDGE

    def send_change_login(self, *none):

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        login = pph('] Current:')
        self.pipe_out.put(pf.do_login_change % (login.encode(CNF.SRM_ENC), pph("] New:").encode(CNF.SRM_ENC)))
        del login

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def send_reset(self, opts: tuple):

        mod = opts[0]

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        self.pipe_out.put(pf.reset % mod.encode(CNF.SRM_ENC))

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def send_shutdown(self):

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        self.pipe_out.put(pf.shutdown)

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break

    def send_kill(self):

        self.pipe_out.put(pf.kill)

    def send_err(self, dat: str="ERROR"):

        if self.BRIDGE.header: self.BRIDGE.header.option_list = None
        self.BRIDGE.bridge_lock = True

        self.pipe_out.put(self.ierr % dat.encode(CNF.SRM_ENC))

        for _ in range(CNF.RESPONSE_TIMEOUT):
            sleep(CNF.RESPONSE_TIMEOUT_ADJUST)
            if not self.BRIDGE.bridge_lock: break
