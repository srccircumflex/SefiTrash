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


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import asctime, time
from sys import stderr
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, timeout
from re import search, sub
from functools import lru_cache
from os import stat, access
from gzip import open as gzipopen
from shutil import copyfileobj
from string import ascii_lowercase
from threading import RLock

from sec.fscModule import FStreamCipher
from _rc import configurations as CNF

import logging
logging._levelToName = CNF.LEVEL_TO_NAME
from logging import basicConfig, Formatter, FileHandler, StreamHandler, getLogger

basicConfig(filename=CNF.LOG_BASIC_FILE, level=0)


def log_bad_data(ip:str, __socket, header:bytes=None):

    _logname = asctime().replace(' ', '-') + '_' + ip + ".gz"
    if CNF.SYS_PLATFORM == "w": _logname = _logname.replace(':', '.')

    chars = {
        b'#' : b'---##SHARP##---',
        b'^' : b'_##BUFFER##_  ',
        b'\n': b'---##NEWLN##---',
        b'\t': b'---##TAP##---',
        b'\r': b'---##RETURN##---',
        b'\\\\': b'---##ESCAPESEQ##---',
        b'$' : b'\n'
    }

    def _escape(dat):
        for char in chars: dat = sub(char, chars[char], dat)
        return dat

    with gzipopen(CNF.LOGPATH_TOXIC_DATA + '/' + _logname, 'wb', compresslevel=9) as f:
        if header is not None:
            f.write(b'\n###___________________________HEAD___________________________\n' + header + b'\n')
        f.write(b'\n###___________________________DATA___________________________\n')
        try:
            for _ in CNF.BUFFER_ITER(CNF.MAXSIZE_TOXICS, 64):
                data = __socket.recv(64)
                if not data: break
                f.write(_escape(data))
        except OSError as err:
            f.write(str((err, err.errno)).encode(CNF.LOC_ENC, errors="replace"))
        f.write(b'\n##___________________________[EOD]___________________________\n')


class MailAlert:

    exp_count = 0
    exp_loglim = 10

    def __init__(self):

        self._lock = RLock()

        if CNF.MAIL_FSC:
            # check login
            try:
                if CNF.MAIL_CRYPT == 'SSL':
                    with smtplib.SMTP_SSL(
                            CNF.MAIL_SMTP_ADDR,
                            CNF.MAIL_SMTP_PORT,
                            context=CNF._MAIL_SSL
                    ) as server:
                        server.login(CNF.MAIL_USER, password=self._getpw())

                elif CNF.MAIL_CRYPT == 'TLS':
                    with smtplib.SMTP(
                            CNF.MAIL_SMTP_ADDR,
                            CNF.MAIL_SMTP_PORT
                    ) as server:
                        server.starttls(context=CNF._MAIL_SSL)
                        server.login(CNF.MAIL_USER, password=self._getpw())

            except Exception as e:
                if not CNF.CONFIGURE_:
                    print(f"MailLoginError %s %s" % (type(e), e))
                    CNF.EXP_EXIT(1)
                raise e

    @staticmethod
    def _getpw():
        with open(CNF.MAIL_XF % CNF.USER, "rb") as f:
            return FStreamCipher(f.read(), CNF.MAIL_XFSEED, *CNF.MAIL_FSC).decrypt().decode('ISO-8859-1')

    def write(self, msg: str):
        if not CNF.MAIL_FSC: return
        try:
            self._lock.acquire(timeout=2)

            message = MIMEMultipart()
            message["From"] = CNF.MAIL_SENDER_MAIL
            message["To"] = CNF.MAIL_RECEIVER_MAIL
            if CNF.MAIL_BCC: message["Bcc"] = CNF.MAIL_BCC
            message["Subject"] = "SefiTrash  __  ALERT -%s-  __" % msg.strip()[-2:]
            message.attach(MIMEText(msg, "plain"))
            message.attach(MIMEText(f"[{asctime()}] message from SefiTrash <%s 0x%x>" % (self.write.__qualname__, self.__hash__()), "plain"))

            try:
                if CNF.MAIL_CRYPT == 'SSL':
                    with smtplib.SMTP_SSL(
                            CNF.MAIL_SMTP_ADDR,
                            CNF.MAIL_SMTP_PORT,
                            context=CNF._MAIL_SSL
                    ) as server:
                        server.login(CNF.MAIL_SENDER_MAIL, password=self._getpw())
                        server.sendmail(
                            CNF.MAIL_SENDER_MAIL,
                            CNF.MAIL_RECEIVER_MAIL,
                            message.as_string()
                        )

                elif CNF.MAIL_CRYPT == 'TLS':
                    with smtplib.SMTP(
                            CNF.MAIL_SMTP_ADDR,
                            CNF.MAIL_SMTP_PORT
                    ) as server:
                        server.starttls(context=CNF._MAIL_SSL)
                        server.login(CNF.MAIL_SENDER_MAIL, password=self._getpw())
                        server.sendmail(
                            CNF.MAIL_SENDER_MAIL,
                            CNF.MAIL_RECEIVER_MAIL,
                            message.as_string()
                        )
            except Exception as err:
                if self.exp_count < self.exp_loglim:
                    LOGS_.blackbox.logg(60, f"|--[ LOGGING MAILALERT ERROR ]--|[ {type(err)} ]|", ico='/\\\\\\\\\\/')
                    print(f"[/\\\\\\\\\\/]|--[ LOGGING MAILALERT ERROR ]--|[ {type(err)} ]|", file=stderr)
                    with open(CNF.LOG_LOGSTREAMERR, 'a') as f: f.write(f"{asctime()} : {type(err)} {err} {err.__traceback__.tb_frame} ; {msg=}\n")
                    self.exp_count += 1
        finally:
            self._lock.release()


class NoneAlert:
    def __init__(self): pass
    def write(self, *args, **kwargs) -> None: pass

mailalert = NoneAlert()
if CNF.HOST_SIDE and not (CNF.LATERAL_ or CNF.CONFIGURE_):
    mailalert = MailAlert()


class BASE:

    _basicFileFormat = {'fmt':"%(asctime)s : %(levelname)-8s : (%(ip)-15s|%(cache)-15s) %(message)s %(mt)s"}
    _basicMailFormat = {'fmt':"%(asctime)s : %(levelname)-8s\n"
                              "(%(ip)-15s|%(cache)-15s) %(mt)s\n"
                              "%(message)s\n"
                              "[-EOF-%(levelno)-2s"}
    _basicStreamFormat = CNF.STREAM_FORMAT

    _fileFORM = Formatter(**_basicFileFormat)
    _strmFORM = Formatter(**_basicStreamFormat)
    _mailFORM = Formatter(**_basicMailFormat)

    _gzipcount = 0
    _mkgzipat = 100

    def __init__(self):
        self._extras = {'ip': "", 'cache': "", 'mt': "", '_ms': "", 'ico': ""}

    def _logcounter(self, _logs: list):
        self._gzipcount += 1
        if self._gzipcount >= self._mkgzipat:
            self._gzipcount = 0
            self._mkgzipif(_logs)

    def _mkgzipif(self, _logs: list):
        for _lf in _logs:
            for _handl in _lf.handlers:
                if isinstance(_handl, FileHandler):
                    if stat((_lfp := _handl.stream.name)).st_size >= CNF.LOGMAX_LOGSIZE:
                        _exist = [0, ""]
                        _m = 1; _idx = -1
                        for _it in range(CNF.LOGMAX_BACKUPS):
                            _idx += 1
                            if _idx == 26:
                                _m += 1; _idx = 0
                            if access((_bu := f"{_lfp}-{ascii_lowercase[_idx] * _m}.gz"), 0):
                                if _t := stat(_bu).st_mtime < _exist[0]:
                                    _exist[0] = _t
                                    _exist[1] = _bu
                            else:
                                _exist = [0, ""]
                                with open(_lfp, "rb") as lf:
                                    with gzipopen(_bu, "wb", compresslevel=9) as gf:
                                        _log = lf.read()
                                        copyfileobj(lf, gf)
                                with open(_lfp, "wb") as f:
                                    [f.write(ln + b'\n') for ln in _log.splitlines()[-3:]]
                                break
                        if _exist[0]:
                            with open(_lfp, "rb") as lf:
                                with gzipopen(_exist[1], "wb", compresslevel=9) as gf:
                                    _log = lf.read()
                                    copyfileobj(lf, gf)
                            with open(_lfp, "wb") as f:
                                [f.write(ln + b'\n') for ln in _log.splitlines()[-3:]]
                            _exist = [0, ""]

    @lru_cache(20)
    def _mk_extra(self, ip:str, cache:str, mt:str):
        if ip != "": self._extras |= {'ip': ip}
        if cache != "": self._extras |= {'cache': cache.replace(' ', '')}
        if mt != "": self._extras |= {'mt': f"<{mt}>"}

    def _mk_extras(self, ip:str, cache:dict, mt):
        self._mk_extra(ip, (
            str(cache.get(ip)) if cache is not None else ""
        ), (
            str(mt.__qualname__) if mt is not None else ""
        ))

    def _do_log(self, __log, lv:int, msg:str, *args, ico:str="", ansi:str=""):
        for arg in args: msg += f" {arg} "
        self._extras |= {'_ms': sub("^[0-9]+[^.]", "", "{:.3f}".format(time())), 'ico': ico,
                         'ansi_msg': ansi + msg + '\x1b[0m', 'ansi_pr': CNF.LEVEL_TO_ANSI_PREFIX.get(lv),
                         'ansi_lv': CNF.LEVEL_TO_ANSI_NAME.get(lv)}
        __log.log(lv, msg, extra=self._extras)
        self._logcounter([__log])


class _BLACKBOX(BASE):
    handler_F = FileHandler(CNF.LOG_BLACKBOX)
    handler_S = StreamHandler(stderr)
    handler_F.setFormatter(BASE._fileFORM)
    handler_S.setFormatter(BASE._strmFORM)
    handler_F.setLevel(CNF.LOGLV_BLACKBOX[1])
    handler_S.setLevel(CNF.LOGLV_BLACKBOX[0])

    handler_M = StreamHandler(mailalert)
    handler_M.setFormatter(BASE._mailFORM)
    handler_M.setLevel(CNF.MAILALERTLV_BLACKBOX)

    def __init__(self):
        BASE.__init__(self)
        self._log = getLogger('BX')
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_S)
        self._log.addHandler(self.handler_M)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _FirewallLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_FIREWALL)
    handler_s = StreamHandler(stderr)
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)
    handler_f.setLevel(CNF.LOGLV_FIREWALL[1])
    handler_s.setLevel(CNF.LOGLV_FIREWALL[0])

    handler_m = StreamHandler(mailalert)
    handler_m.setFormatter(BASE._mailFORM)
    handler_m.setLevel(CNF.MAILALERTLV_FIREWALL)

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('FW')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)
        self._log.addHandler(self.handler_m)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _CallLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_CALL)
    handler_s = StreamHandler(stderr)
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)
    handler_f.setLevel(CNF.LOGLV_CALL[1])
    handler_s.setLevel(CNF.LOGLV_CALL[0])

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('CL')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _PathLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_PATH)
    handler_s = StreamHandler(stderr)
    handler_f.setLevel(CNF.LOGLV_PATH[1])
    handler_s.setLevel(CNF.LOGLV_PATH[0])
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('PH')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _BridgeLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_BRIDGE)
    handler_s = StreamHandler(stderr)
    handler_f.setLevel(CNF.LOGLV_BRIDGE[1])
    handler_s.setLevel(CNF.LOGLV_BRIDGE[0])
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('BR')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _SockIOLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_SOCKIO)
    handler_s = StreamHandler(stderr)
    handler_f.setLevel(CNF.LOGLV_SOCKIO[1])
    handler_s.setLevel(CNF.LOGLV_SOCKIO[0])
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('IO')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, mt=None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=mt)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class _KillLog(_BLACKBOX):
    handler_f = FileHandler(CNF.LOG_KILL)
    handler_s = StreamHandler(stderr)
    handler_f.setLevel(CNF.LOGLV_KILL[1])
    handler_s.setLevel(CNF.LOGLV_KILL[0])
    handler_f.setFormatter(BASE._fileFORM)
    handler_s.setFormatter(BASE._strmFORM)

    def __init__(self):
        _BLACKBOX.__init__(self)
        self._log = getLogger('KL')
        self._log.addHandler(self.handler_f)
        self._log.addHandler(self.handler_F)
        self._log.addHandler(self.handler_s)

    def logg(self, lv: int, msg, *args, ip: str = "", cache: dict = None, ico: str = "", ansi: str = ""):
        self._mk_extras(ip=ip, cache=cache, mt=None)
        self._do_log(self._log, lv, str(msg), *args, ico=ico, ansi=ansi)


class SockStream:

    exp_count = 0
    exp_loglim = 10

    def __init__(self):

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.settimeout(.2)
        self.sock.bind(CNF.INSPECT_BINDING)
        self.sock.listen(1)
        self._s = None

    def flush(self, *args, **kwargs) -> None: pass

    def write(self, dat):
        if self._s:
            try:
                return self._s.sendall(dat.encode(CNF.LOG_ENC, errors="replace"))
            except ConnectionError:
                pass
            except Exception as err:
                if self.exp_count < self.exp_loglim:
                    print(f"[/\\\\\\\\\\/]|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", file=stderr)
                    LOGS_.blackbox.logg(60, f"|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", ico='/\\\\\\\\\\/')
                    with open(CNF.LOG_LOGSTREAMERR, 'a') as f: f.write(f"{asctime()} : {type(err)} {err} {err.__traceback__.tb_frame} ; {dat=}\n")
                    self.exp_count += 1
        try:
            self._s, _ = self.sock.accept()
            self._s.sendall(dat.encode(CNF.LOG_ENC, errors="replace"))
        except timeout:
            return
        except OSError as err:
            if err.errno != 11:
                if self.exp_count < self.exp_loglim:
                    print(f"[/\\\\\\\\\\/]|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", file=stderr)
                    LOGS_.blackbox.logg(60, f"|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", ico='/\\\\\\\\\\/')
                    with open(CNF.LOG_LOGSTREAMERR, 'a') as f: f.write(f"{asctime()} : {type(err)} {err} {err.__traceback__.tb_frame} ; {dat=}\n")
                    self.exp_count += 1
        except Exception as err:
            if self.exp_count < self.exp_loglim:
                print(f"[/\\\\\\\\\\/]|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", file=stderr)
                LOGS_.blackbox.logg(60, f"|--[ LOGGING SOCKSTREAM ERROR ]--|[ {type(err)} ]|", ico='/\\\\\\\\\\/')
                with open(CNF.LOG_LOGSTREAMERR, 'a') as f: f.write(f"{asctime()} : {type(err)} {err} {err.__traceback__.tb_frame} ; {dat=}\n")
                self.exp_count += 1

    def close(self):
        try:
            self.sock.close()
        except OSError as err:
            with open(CNF.LOG_LOGSTREAMERR, 'a') as f: f.write(f"{asctime()} : {type(err)} {err} {err.__traceback__.tb_frame}\n")

    def __del__(self):
        self.close()


class LOGS:

    if not CNF.LATERAL_ and CNF.INSPECT_BINDING:
        _sockstream = SockStream()
        _sockhandler = StreamHandler(_sockstream)
        _sockhandler.setLevel(20)
        _sockfrmt = Formatter(**CNF.STREAM_FORMAT)
        _sockhandler.setFormatter(_sockfrmt)

    def __init__(self):

        self.blackbox = _BLACKBOX()
        self.firewall = _FirewallLog()
        self.call = _CallLog()
        self.path = _PathLog()
        self.bridge = _BridgeLog()
        self.sockio = _SockIOLog()
        self.kill = _KillLog()

        self.blackbox._mkgzipif([self.blackbox._log, self.firewall._log, self.call._log, self.path._log,
                                 self.bridge._log, self.sockio._log, self.kill._log])

    def _closeSockstream(self): self._sockstream.close()

    def _setSockstream(self, lv:str=None):
        if not CNF.INSPECT_BINDING: raise AttributeError(f"{CNF.INSPECT_BINDING=}")
        if lv and search("^[0-9]+$", lv.strip()): self._sockhandler.setLevel(int(lv))
        elif lv: raise ValueError(f"{lv=}")
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            _handl = 'handler_s'
            if _attr == "blackbox":
                if not CNF.MOD_BGSTREAM: continue
                _handl = 'handler_S'
            exec(f"self.{_attr}._log.removeHandler(self.{_attr}.{_handl})")
            exec(f"self.{_attr}._log.addHandler(self._sockhandler)")

    def _resetIOStream(self):
        if CNF.HOST_SIDE and not CNF.MOD_BGSTREAM: raise AttributeError(f"{CNF.MOD_BGSTREAM=}")
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            _handl = 'handler_s'
            if _attr == "blackbox":
                if not CNF.MOD_BGSTREAM: continue
                _handl = 'handler_S'
            exec(f"self.{_attr}._log.removeHandler(self._sockhandler)")
            exec(f"self.{_attr}._log.addHandler(self.{_attr}.{_handl})")

    def _setLVstoDebug(self):
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            if _attr == "blackbox": continue
            exec(f"self.{_attr}.handler_s.setLevel(0)")
        self.blackbox.handler_S.setLevel(0)

    def _resetCNFLV(self):
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            if _attr == "blackbox": continue
            exec("self.%s.handler_s.setLevel(%d)" % (_attr, getattr(CNF, f"LOGLV_{_attr.upper()}")[0]))
            exec("self.%s.handler_f.setLevel(%d)" % (_attr, getattr(CNF, f"LOGLV_{_attr.upper()}")[1]))
        self.blackbox.handler_S.setLevel(getattr(CNF, f"LOGLV_BLACKBOX")[0])
        self.blackbox.handler_F.setLevel(getattr(CNF, f"LOGLV_BLACKBOX")[1])

    def _allSLVsto(self, lv: int):
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            if _attr == "blackbox": continue
            exec("self.%s.handler_s.setLevel(%d)" % (_attr, lv))

    def _allFLVsto(self, lv: int):
        for _attr in self.__dict__:
            if _attr.startswith('_'): continue
            if _attr == "blackbox": continue
            exec("self.%s.handler_f.setLevel(%d)" % (_attr, lv))

    def _enableBlackbox(self): self.blackbox.handler_F.setLevel(0)

    def CNSentry(self, opts: tuple=None, lv:str=None):
        if opts is None:
            from pprint import pprint
            for _attr in self.__dict__:
                if _attr.startswith('_'): continue
                exec('pprint(f"{self.%s._log.handlers=}")' % _attr)
            return
        if 'sockclose' in opts[1]: return self._closeSockstream()
        if 'sock' in opts[1]: return self._setSockstream(lv)
        if 'io' in opts[1]: return self._resetIOStream()
        if 'debug' in opts[1]: return self._setLVstoDebug()
        if 'reset' in opts[1]: return self._resetCNFLV()
        if 'allS' in opts[1]:
            if search("^[0-9]+$", lv.strip()): return self._allSLVsto(int(lv))
            else: raise ValueError(f"{lv=}")
        if 'allF' in opts[1]:
            if search("^[0-9]+$", lv.strip()): return self._allFLVsto(int(lv))
            else: raise ValueError(f"{lv=}")
        if 'blackbox' in opts[1]: return self._enableBlackbox()


LOGS_ = LOGS()
