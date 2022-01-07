from sec import fscFunction, fscIO
from sys import stdout, stderr
from time import time

coding_a = 'ISO-8859-1'
bench_out = stderr

class FStreamCipher:

    def __init__(self, ib:bytes, seed:str, ilv:int=0, pp:tuple=(0, 1), hps:int=3, v:str=None):
        global coding_a
        self.enc = coding_a
        self.ib = ib
        self.sd = seed

        self.ilv = 256 + ilv
        self.pp = pp
        self.hps = hps

        self.v = v
        if v:
            self.vp0 = (True if 'p' in v else False)
            self.vp1 = (True if 'v' in v else False)
            self.vp2 = (True if 'P' in v else False)
            self.vb1 = (True if 'b' in v else False)
            self.tst = (True if 't' in v else False)

    def enc_vlv2(self):
        if self.vb1: t = time()
        print(" [+] involve InitializationVector", end="", file=stdout)
        self.ib = fscFunction.init_vec(self.ib, self.ilv)
        print(" _DONE_", file=stdout)
        print(" [+] Transposition", end=(" " if self.vp0 else '\n'), file=stdout)
        srm, bas = fscFunction.transposition(self.sd, self.ib, part_prio=self.pp, hps=self.hps, ilv=self.ilv,
                                             vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)
        if self.tst: fscIO.to_stderr(bas, srm)
        print(" [+] StreamCiphering", end="", file=stdout)
        o = fscFunction.x_stream(srm, bas)
        print(" _DONE_", file=stdout)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return o

    def enc_vlv1(self):
        if self.vb1: t = time()
        self.ib = fscFunction.init_vec(self.ib, self.ilv)
        srm, bas = fscFunction.transposition(self.sd, self.ib, part_prio=self.pp, hps=self.hps, ilv=self.ilv,
                                             vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)
        if self.tst: fscIO.to_stderr(bas, srm)
        o = fscFunction.x_stream(srm, bas)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return o

    def enc_vlv0(self):
        return fscFunction.x_stream(
            *fscFunction.transposition(
                self.sd, fscFunction.init_vec(
                    self.ib, self.ilv
                ),
                part_prio=self.pp, hps=self.hps, ilv=self.ilv, vp0=False, vp2=False, vb1=False
            )
        )

    def dec_vlv2(self):
        if self.vb1: t = time()
        print(" [+] StreamGenerate ", end="", file=stdout)
        l0 = len(self.ib) - 128
        pr = l0 // 10
        srm = ""
        gst = fscFunction.GSTool(fscFunction.gen_stream(self.sd, l0), self.pp)
        for n in range(l0):
            srm += gst.srm(n)
            (print("|", end="", file=stdout, flush=True) if self.vp0 and not n % pr else None)
        for n in range(128): srm += gst.srm(n)
        print(" _DONE_", end=("" if self.vb1 else "\n"), file=stdout)
        if self.vb1: print(f" -$ {time() - t} s", file=bench_out)
        print(" [+] StreamCiphering", end="", file=stdout)
        o = fscFunction.x_stream(bytearray(srm, self.enc), self.ib)
        print(" _DONE_\n [+] Transposition", end=(" " if self.vp0 else '\n'), file=stdout)
        bas = fscFunction.transposition(self.sd, o, part_prio=self.pp, hps=self.hps, de_=True,
                                        vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)[1]
        print(" [+] remove InitializationVector", end="", file=stdout)
        bas = fscFunction.init_vec(bas, ilv=self.ilv, rm=True)
        print(" _DONE_", file=stdout)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return bas

    def dec_vlv1(self):
        if self.vb1: t = time()
        l0 = len(self.ib) - 128 * self.hps
        gst = fscFunction.GSTool(fscFunction.gen_stream(self.sd, l0), self.pp)
        pr = l0 // 10
        srm = ""
        for n in range(l0):
            srm += gst.srm(n)
            (print("|", end="", file=stdout, flush=True) if self.vp0 and not n % pr else None)
        for n in range(128 * self.hps): srm += gst.srm(n)
        if self.vb1: print(f" -$ {time() - t} s", file=bench_out)
        o = fscFunction.x_stream(bytearray(srm, self.enc), self.ib)
        bas = fscFunction.transposition(self.sd, o, part_prio=self.pp, hps=self.hps, de_=True,
                                        vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)[1]
        bas = fscFunction.init_vec(bas, ilv=self.ilv, rm=True)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return bas

    def dec_vlv0(self):
        l0 = len(self.ib) - 128 * self.hps
        gst = fscFunction.GSTool(fscFunction.gen_stream(self.sd, l0), self.pp)
        srm = ""
        return fscFunction.init_vec(
            fscFunction.transposition(
                self.sd, fscFunction.x_stream(
                    bytearray(srm.join(
                        [gst.srm(n) for n in range(l0)]
                        + [gst.srm(n) for n in range(128 * self.hps)]
                    ), self.enc),
                    self.ib
                ),
                part_prio=self.pp, hps=self.hps, de_=True, vp0=False, vp2=False, vb1=False
            )[1],
            ilv=self.ilv, rm=True
        )

    def Dec_vlv2(self):
        if self.vb1: t = time()
        l0 = len(self.ib) - 128 * self.hps
        pr = l0 // 10
        srm = ""
        pos = []
        gen_pos = fscFunction.basis_and_pos(l0, self.hps)
        gen_srm = fscFunction.gen_stream(self.sd, l0)
        gst = fscFunction.GSTool(gen_srm, self.pp)
        pst = fscFunction.PSTool(gen_pos, gen_srm, self.pp)
        next(gen_pos)
        for n in range(l0):
            p, s = pst.pos_srm(n)
            srm += s
            pos.append(p)
            (print("|", end="", file=stdout, flush=True) if self.vp0 and not n % pr else None)
        for n in range(128 * self.hps): srm += gst.srm(n)
        print(" _DONE_", end=("" if self.vb1 else "\n"), file=stdout)
        if self.vb1: print(f" -$ {time() - t} s", file=bench_out)
        print(" [+] StreamCiphering", end="", file=stdout)
        o = fscFunction.x_stream(bytearray(srm, self.enc), self.ib)
        print(" _DONE_\n [+] Transposition", end=(" " if self.vp0 else '\n'), file=stdout)
        bas = fscFunction.transposition(self.sd, o, part_prio=self.pp, hps=self.hps, de_=pos,
                                        vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)[1]
        print(" [+] remove InitializationVector", end="", file=stdout)
        bas = fscFunction.init_vec(bas, ilv=self.ilv, rm=True)
        print(" _DONE_", file=stdout)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return bas

    def Dec_vlv1(self):
        if self.vb1: t = time()
        l0 = len(self.ib) - 128 * self.hps
        pr = l0 // 10
        srm = ""
        pos = []
        gen_pos = fscFunction.basis_and_pos(l0, self.hps)
        gen_srm = fscFunction.gen_stream(self.sd, l0)
        gst = fscFunction.GSTool(gen_srm, self.pp)
        pst = fscFunction.PSTool(gen_pos, gen_srm, self.pp)
        next(gen_pos)
        for n in range(l0):
            p, s = pst.pos_srm(n)
            srm += s
            pos.append(p)
            (print("|", end="", file=stdout, flush=True) if self.vp0 and not n % pr else None)
        for n in range(128 * self.hps): srm += gst.srm(n)
        if self.vb1: print(f" -$ {time() - t} s", file=bench_out)
        bas = fscFunction.transposition(
            self.sd, fscFunction.x_stream(
                bytearray(srm, self.enc), self.ib
            ), part_prio=self.pp, hps=self.hps, de_=pos, vp0=self.vp0, vp2=self.vp2, vb1=self.vb1)[1]
        bas = fscFunction.init_vec(bas, ilv=self.ilv, rm=True)
        if self.vb1: print(f"—————————————————————————————————\n"
                           f"-$$ {time() - t} s", file=bench_out)
        return bas

    def Dec_vlv0(self):
        l0 = len(self.ib) - 128 * self.hps
        srm = ""
        pos = []
        gen_pos = fscFunction.basis_and_pos(l0, self.hps)
        gen_srm = fscFunction.gen_stream(self.sd, l0)
        gst = fscFunction.GSTool(gen_srm, self.pp)
        pst = fscFunction.PSTool(gen_pos, gen_srm, self.pp)
        next(gen_pos)
        for n in range(l0):
            p, s = pst.pos_srm(n)
            pos.append(p)
            srm += s
        for n in range(128 * self.hps): srm += gst.srm(n)
        return fscFunction.init_vec(
            fscFunction.transposition(
                self.sd, fscFunction.x_stream(
                    bytearray(srm, self.enc),
                    self.ib
                ),
                part_prio=self.pp, hps=self.hps, de_=pos, vp0=False, vp2=False, vb1=False
            )[1],
            ilv=self.ilv, rm=True
        )

    def encrypt(self):
        if self.v:
            if self.vp1:
                return self.enc_vlv2()
            else:
                return self.enc_vlv1()
        else:
            return self.enc_vlv0()

    def decrypt(self, pos_cache:bool=False):
        if pos_cache:
            if self.v:
                if self.vp1:
                    return self.Dec_vlv2()
                else:
                    return self.Dec_vlv1()
            else:
                return self.Dec_vlv0()
        else:
            if self.v:
                if self.vp1:
                    return self.dec_vlv2()
                else:
                    return self.dec_vlv1()
            else:
                return self.dec_vlv0()
