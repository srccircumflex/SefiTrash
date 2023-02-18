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


from . import SGRAttr
from . import Colors
from . import _ctrl_seq


ControlSequence = _ctrl_seq.ControlSequence

_Win32AnsiOutInstance = False
_shutdown = False
disabled = False
_init = False

def InitWin32Ansi(raise_error: bool = True, ignore_err: bool = True):
    global _Win32AnsiOutInstance, _shutdown, _init
    if _init: return
    _init = True
    from sys import platform
    if platform != "win32": return
    import ctypes
    kernel32 = ctypes.windll.kernel32
    winbase_h_stdout = -11
    winbase_h_stderr = -12
    _sout = kernel32.SetConsoleMode(kernel32.GetStdHandle(winbase_h_stdout), 7)
    _serr = kernel32.SetConsoleMode(kernel32.GetStdHandle(winbase_h_stderr), 7)
    if not _sout + _serr:
        if raise_error:
            raise EnvironmentError(f"""
            kernel32.SetConsoleMode(stdout, ENABLE_VIRTUAL_TERMINAL_PROCESSING) -> {_sout}
            kernel32.SetConsoleMode(stderr, ENABLE_VIRTUAL_TERMINAL_PROCESSING) -> {_serr} 
            """)
        else:
            if not ignore_err:
                _shutdown = True
                _ctrl_seq._shutdown = True


class ESC:
    octal = "\033"
    hexadecimal = "\x1b"
    unicode = "\u001b"
    ControlSequenceIntroducer = CSI = "["

    class _WinE:
        decimal = "27"
        ctrl_key = "^["
        powershell = "$([char]27)"
        e = "`e"
        regedit = r"REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1"
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        _ENABLE_VIRTUAL_TERMINAL_PROCESSING = 7


class SelectGraphicRendition:

    def __init__(self, __esc: str = ESC.unicode,
                 _disabled: bool = False,
                 raise_initerr: bool = True,
                 ignore_initerr: bool = True):

        global disabled, SGRInstance
        disabled = _disabled
        self.esc = _ctrl_seq.esc = __esc
        self.reset = self.esc + ESC.ControlSequenceIntroducer + 'm'
        InitWin32Ansi(raise_initerr, ignore_initerr)
        if not SGRInstance: SGRInstance = self

    def get(self, *sgr: str) -> str:
        if not sgr or disabled or _shutdown: return ""
        return self.esc + ESC.ControlSequenceIntroducer + str().join([a for a in sgr])[:-1] + 'm'

    def wrap(self, __str: str, *sgr: str) -> str:
        if disabled or _shutdown: return __str
        return self.get(*sgr) + __str + self.reset

    @staticmethod
    def disable():
        global disabled
        disabled = True

    @staticmethod
    def enable():
        global disabled
        disabled = False


def disable():
    global disabled
    disabled = True
    ControlSequence.disable()


def enable():
    global disabled
    disabled = False
    ControlSequence.enable()

SGRInstance: SelectGraphicRendition = None
CSInstance: ControlSequence = None

