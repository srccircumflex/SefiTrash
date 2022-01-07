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


from os import urandom
from random import randint
from time import time
from re import search, sub

from _rc import configurations as CNF
from sec.fscModule import FStreamCipher
from sec.fscIO import pph

def _mk_salt(user: str, login:str) -> tuple[str, int, tuple[int, int], int]:
    with open(CNF.AUTH_CONF[user]['spc'], 'wb') as f:
        slt = str().join([chr(randint(33,127)) for _ in range(5)])
        ilv = ord(urandom(1)) * 2
        prt = ord(urandom(1)) % 2
        pri = randint(1,3)
        hps = randint(3,10)
        f.write(
            FStreamCipher(
                f"{int(time())} {slt} {ilv} ({prt},{pri}) {hps}".encode(CNF.LOC_ENC), login, *CNF.AUTH_CONF[user]['bpp']
            ).encrypt()
        )
    with open(CNF.AUTH_CONF[user]['ppp'], 'wb') as f:
        f.write(
            FStreamCipher(
                f"{ilv} {prt} {pri} {hps}".encode(CNF.LOC_ENC), login, *CNF.AUTH_CONF[user]['bpp']
            ).encrypt()
        )
    return slt, ilv, (prt,pri), hps


def _mk_hands_table(user:str, *args) -> None:
    with open(CNF.AUTH_CONF[user]['hst'], 'wb') as f:
        f.write(
            FStreamCipher(
                b''.join([
                    b'%b\n' % b''.join([
                        b'%d%d%d%d ' % (ord(urandom(1)), ord(urandom(1)), ord(urandom(1)), ord(urandom(1))) for _ in
                        range(24)
                    ]) for _ in range(31)
                ]), *args
            ).encrypt()
        )


def mk_login(user:str, login:str = None) -> None:
    login = (pph() if login is None else login)
    slt, ilv, p_p, hps = _mk_salt(user, login)
    _mk_hands_table(user, login, ilv, p_p, hps)
    with open(CNF.AUTH_CONF[user]['lin'], 'wb') as f:
        f.write(
            FStreamCipher(login.encode(CNF.LOC_ENC), slt + login, ilv, p_p, hps).encrypt()
        )


def _rcDELUser(user: str):
    with open(CNF.BOARD_USERS, "r") as f: _conflns = f.read().splitlines()
    with open(CNF.BOARD_USERS, "w") as f:
        for _ln in _conflns:
            if _s := search("^" + user + "\s.*", _ln):
                _ln = sub(_s.group(), _s.group() + '  <del>', _ln)
            f.write(_ln + '\n')

def _rcUDELUser(user: str):
    with open(CNF.BOARD_USERS, "r") as f: _conflns = f.read().splitlines()
    with open(CNF.BOARD_USERS, "w") as f:
        for _ln in _conflns:
            if _s := search("^" + user + "\s.*", _ln): _ln = sub(_s.group(), sub('<del>', '', _s.group()), _ln)
            f.write(_ln + '\n')
