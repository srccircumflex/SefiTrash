from hashlib import sha256, sha224, sha512
from getpass import getpass
from sys import stdout, stderr
from os import urandom, access, stat, R_OK, path

coding_a: str = 'iso-8859-1'
coding_b: str = 'utf-8'
block: int = 10485760

def pph(prompt:str= " Password:", sha:str= '256') -> str:
    global coding_a
    try:
        return (sha256(bytearray(getpass(prompt), coding_a)).hexdigest() if sha == '256'
                else sha224(bytearray(getpass(prompt), coding_a)).hexdigest() if sha == '224'
                else sha512(bytearray(getpass(prompt), coding_a)).hexdigest() if sha == '512'
                else exit(f"sha{256,244,512} : \n>> {type(sha)}:{sha}"))
    except KeyboardInterrupt:
        print("^C", file=stderr)
        raise KeyboardInterrupt


def hb_stdin(prompt:str= " h/") -> bytes:
    global coding_a
    return bytearray(getpass(prompt), coding_a)


g_file: str = None
def gen_rb_file(v:bool, ivb:int):
    global g_file, coding_a
    sectors: int = (stat(g_file).st_size // (block + ivb)) + 1
    i: int = 1
    print(f" [:] {sectors} Iterations", file=stdout)
    with open(g_file, "rb") as f:
        while True:
            c = f.read(block + ivb)
            if c == b'': break
            print(f" [:] Iteration {i} / {sectors}", file=stdout); i += 1
            yield c


def rb_file(file:str, ivb:int) -> (bytes, int):
    global g_file, coding_a
    try:
        if not path.isfile(file): raise FileNotFoundError
        if not access(file, R_OK): exit(f"PermissionError :'{file}'")
        if stat(file).st_size > block + ivb:
            g_file = file
            return -3
        with open(file, "rb") as f:
            return f.read()
    except FileNotFoundError:
        exit(f"FileNotFoundError :'{file}'")


EOF: str = None
def b_stdin(EOF_:str= '@EOF') -> bytes:
    global EOF, coding_a
    EOF_ = (EOF if EOF else EOF_)
    try:
        print(f"~[  {EOF_}  ]", file=stdout)
        CAT_s: str = ""
        while True:
            print("..> ", file=stdout, end='')
            CAT_i = f'{input()}\n'
            if CAT_i == f"{EOF_}\n":
                break
            CAT_s += CAT_i
        return bytearray(CAT_s[:-1], coding_a)
    except Exception as e:
        exit(e)


def multi_hash(file:str, mk:bool=True, prompt:str= " Password:", ilv:int=256) -> str:
    global coding_a
    try:
        if mk:
            with open(file, "wb") as f: f.write(urandom(ilv))
        k: str = ""
        for a, b in zip(bytearray(sha512(open(file, "rb").read()).hexdigest(), coding_a),
                        bytearray(sha512(bytearray(getpass(prompt), coding_a)).hexdigest(), coding_a)):
            k += chr(a ^ b)
        return k
    except FileNotFoundError as e:
        exit(e)


def inject(f:str, inj_b:bytes, chr_r:int=1114111):
    open(f, "ab").write(inj_b)
    l_bM = len(inj_b) % chr_r
    l_bD = len(inj_b) // chr_r
    inj_lL = "\n"
    for _ in range(l_bD): inj_lL += chr(chr_r)
    inj_lL += chr(l_bM)
    open(f, "a").write(inj_lL)


def extract(file:str):
    global coding_b
    inj_lL = open(file, "rb").readlines()[-1]
    l_inj, l_inj_lL = 0, len(inj_lL) + 1
    for c in inj_lL.decode(coding_b): l_inj += ord(c)
    inj_b = open(file, "rb").read()[-(l_inj + l_inj_lL): - l_inj_lL]
    return inj_b

L = False
def to_stderr(b:bytes, srm:bytes=None):
    global coding_a, L
    if srm:
        print(f"\n"
              f"- STREAM -\n"
              f"----------\n"
              f"{srm.decode(coding_a)}\n"
              f"\n"
              f"- FRAGMENTS -", file=stderr)
    if L: print("\n"
                "- CIPHER -", file=stderr)
    print(f"{'-' * 27} ---- --- -- -\n"
          f"{b.decode(coding_a)}\n"
          f"{'-' * 27} ---- --- -- -", file=stderr)
    if srm: L = True
