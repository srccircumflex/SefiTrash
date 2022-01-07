from sys import stdout
from os import urandom
from time import time


coding_a: str = 'ISO-8859-1'
bench_out = stdout


def init_vec(inp: bytes, ilv: int = 256, rm:bool=False) -> bytes:
    if rm:
        return inp[ilv:]
    ap = bytearray()
    ap += urandom(ilv)
    return ap + inp


def basis_and_pos(l0:int, hps:int=3, ilv:int=256):
    l1 = l0 - ilv
    bas = bytearray(); bas += b'0' * (l1 - l1 % 128); bas += urandom(128 * hps + l1 % 128 + ilv); yield bas
    l0 += 128
    for hop in range(hps):
        for sp in range(0, l0 // 128 - 1, hps):             # [4]
            yield sp + hop                                  # [4]


def gen_stream(seed:str, l1:int):
    l0 = len(seed)
    l2 = l1 + 128
    rc = None
    del_ = True
    while True:                                                 # [1]
        l3 = int(str(l2)[-3:])
        if l3 > 111: l2 = l3; break
        l2 = (l2 ** 2) // 7 + l3 + 9
    while True:
        for i in range(len(seed) - 1):                          # [2]
            y = ord(seed[i]) ^ ord(seed[i + 1])
            x = str((y + 1) * (l2 + 1))
            for j in range(len(x) - 3):                         # [3]
                for k in range(2):
                    ri = int(x[j:j + (3 - k)])
                    if ri in range(33, 127):
                        rc = ri
                        break
                if rc:
                    seed += chr(rc)
                    yield rc
                    rc = None
            seed += x[3:4]
            yield y
        if del_:
            del_ = False
            hash_p = seed[l0:]
            del seed
            seed = hash_p


class GSTool:

    def __init__(self, gen_srm, part_prio):
        self.gs = gen_srm
        self.pp = part_prio

    def srm(self, n: int) -> chr:
        pr_0 = next(self.gs)
        pr_1 = next(self.gs)
        prd = {0: pr_0, 1: pr_1}
        if not n % self.pp[1]:
            return chr(prd[self.pp[0]])
        return chr(prd[self.pp[0] ^ 1])


class PSTool:

    def __init__(self, gen_pos, gen_srm, part_prio):
        self.pl = []
        self.m = 0
        self.p = None
        self.gp = gen_pos
        self.gs = gen_srm
        self.pp = part_prio

    def fnd_pos(self) -> int:
        s, a = False, False
        i_ = 0
        for i in range(1, 128):
            j = self.p + i
            if j > 127:
                i_, s = i, True
                break
            if j not in self.pl:
                return j
            j = self.p - i
            if j < 0:
                i_, a = i, True
                break
            if j not in self.pl:
                return j
        if s:
            for i in range(i_, 128):
                j = self.p - i
                if j not in self.pl:
                    return j
        if a:
            for i in range(i_, 128):
                j = self.p + i
                if j not in self.pl:
                    return j

    def pos_srm(self, n: int) -> tuple:
        pr_0 = next(self.gs)                                        # [2]
        pr_1 = next(self.gs)                                        # [2]
        self.p = pr_0 ^ pr_1                                        # [4]
        if len(self.pl) == 128:                                     # [4]
            self.pl.clear()
            self.m = next(self.gp)
        self.p = (self.fnd_pos() if self.p in self.pl else self.p)  # [4]
        self.pl.append(self.p)
        prd = {0: pr_0, 1: pr_1}
        if not n % self.pp[1]:                                      # [2]
            return self.p + 128 * self.m, chr(prd[self.pp[0]])      # [4]
        return self.p + 128 * self.m, chr(prd[self.pp[0] ^ 1])      # [4]


def x_stream(stream, b:bytes) -> bytes:
    global coding_a
    o = bytearray()
    b_stream = (stream if type(stream) == bytes or bytearray else bytearray(stream, coding_a)); del stream
    for s, i in zip(b_stream, b):
        o += bytearray(chr(s ^ i), coding_a)
    del b_stream, b
    return o


def transposition(seed: str, inp_b: bytes, part_prio:tuple[int, int], hps:int=3, ilv:int=256,
                  de_=False, vp0:bool=True, vp2:bool=False, vb1:bool=False) -> tuple:
    global coding_a
    l0 = (len(inp_b) if not de_ else len(inp_b) - 128 * hps)
    if vb1: t = time()
    if vp0 or vp2:
        p_prz, p_prd, x, y, z, N = round(l0 / 100), round(l0 / 10), 0, 0, 10, 0
        vP = (f"{'#' * y}{'_' * z}" if p_prd and vp0 else "")
        P = (f"~[{x}%]{vP} " if p_prz and vp0 else "")
        B = (f" {N} / {l0}" if vp2 else "")
        print(f"{P}{B}", end="", file=stdout)
    if type(de_) != list:
        gen_pos = basis_and_pos(l0, hps, ilv)
        gen_srm = gen_stream(seed, l0)
        gst = GSTool(gen_srm, part_prio)
        pst = PSTool(gen_pos, gen_srm, part_prio)
        if de_: basis = bytearray(); next(gen_pos)
        else: basis = next(gen_pos)
    else: basis = bytearray()
    srm = ""
    if vp0 or vp2:
        if type(de_) == list:
            for n in range(l0):
                if vp2 and n: N = n; B = f" {N} / {l0}"; print(B, end="", file=stdout)
                basis += bytearray(chr(inp_b[de_[n]]), coding_a)
                if vp2: print('\b' * len(B), end="", file=stdout)
                if vp0 and not n % p_prd: y, z = y + 1, z - 1
                if vp0 and p_prz and not n % p_prz:
                    x += 1
                    print('\b' * len(P), end="", file=stdout, flush=True)
                    vP = (f"{'#' * y}{'_' * z}" if p_prd else "")
                    P = f"~[{x}%]{vP} "
                    print(P, end="", file=stdout)
                if vp0 and not p_prz and not vp2 and not n % p_prd: print("|", end="", file=stdout)
        elif type(de_) == bool and de_:
            for n in range(l0):
                if vp2 and n: N = n; B = f" {N} / {l0}"; print(B, end="", file=stdout)
                p, _ = pst.pos_srm(n)
                basis += bytearray(chr(inp_b[p]), coding_a)
                if vp2: print('\b' * len(B), end="", file=stdout)
                if vp0 and not n % p_prd: y, z = y + 1, z - 1
                if vp0 and p_prz and not n % p_prz:
                    x += 1
                    print('\b' * len(P), end="", file=stdout, flush=True)
                    vP = (f"{'#' * y}{'_' * z}" if p_prd else "")
                    P = f"~[{x}%]{vP} "
                    print(P, end="", file=stdout)
                if vp0 and not p_prz and not vp2 and not n % p_prd: print("|", end="", file=stdout)
        else:
            for n in range(l0):
                if vp2 and n: N = n; B = f" {N} / {l0}"; print(B, end="", file=stdout)
                p, s = pst.pos_srm(n)
                basis[p] = inp_b[n]
                srm += s
                if vp2: print('\b' * len(B), end="", file=stdout)
                if vp0 and not n % p_prd: y, z = y + 1, z - 1
                if vp0 and p_prz and not n % p_prz:
                    x += 1
                    print('\b'*len(P), end="", file=stdout, flush=True)
                    vP = (f"{'#' * y}{'_' * z}" if p_prd else ""); P = f"~[{x}%]{vP} "
                    print(P, end="", file=stdout)
                if vp0 and not p_prz and not vp2 and not n % p_prd: print("|", end="", file=stdout)
    else:
        if type(de_) == list:
            for n in range(l0):
                basis += bytearray(chr(inp_b[de_[n]]), coding_a)
        elif type(de_) == bool and de_:
            for n in range(l0):
                if vp2 and n: N = n; B = f" {N} / {l0}"; print(B, end="", file=stdout)
                p, _ = pst.pos_srm(n)
                basis += bytearray(chr(inp_b[p]), coding_a)
        else:
            for n in range(l0):
                p, s = pst.pos_srm(n)
                basis[p] = inp_b[n]
                srm += s
    if not de_:
        for n in range(128 * hps): srm += gst.srm(n)
    if vp0: print(" _DONE_", end=("" if vb1 else "\n"), file=stdout)
    if vb1: print(f" -$ {time() - t} s", file=bench_out)
    if type(de_) != list: gen_pos.close(); gen_srm.close()
    return bytearray(srm, coding_a), basis


#        [1]  |  [2]   |         [3]          [2] |  [4]   |     [5]
# srm # 5 * 5 + 6 * 2n + (3 * ((2 * 3) + 1)) * 2n
# srm # 1 * 1 + 6 * 2n + (0 * ((2 * 3) + 1)) * 2n
# pos # 5 * 5 + 6 * 2n + (3 * ((2 * 3) + 1)) * 2n + 9 * 2n + (~((127 * 6 - 1) + (2))n) * b/128
# pos # 1 * 1 + 6 * 2n + (0 * ((2 * 3) + 1)) * 2n + 9 * 2n + (~(3)n) * b/128

#                                                               # P # T+ ((127 * 6 - 1) + (2))n
#                                                               # P # T- (3)n
