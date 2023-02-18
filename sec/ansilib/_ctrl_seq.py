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

from sys import path as sys_path
from os import path

sys_path.insert(0, path.dirname(path.dirname(__file__)))

import ansilib

sys_path.pop(0)

esc = "\u001b"
disabled = False
_shutdown = False

class ControlSequence:

    class CursorNav:
        @staticmethod
        def Up(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dA" % (esc, n)

        @staticmethod
        def Down(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dB" % (esc, n)

        @staticmethod
        def Forward(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dC" % (esc, n)

        @staticmethod
        def Back(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dD" % (esc, n)

        @staticmethod
        def NextLine(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dE" % (esc, n)

        @staticmethod
        def PreLine(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dF" % (esc, n)

        @staticmethod
        def HorizontAbsolute(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dG" % (esc, n)

        @staticmethod
        def Position(x: int, y: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%d;%dH" % (esc, y, x)

        @staticmethod
        def PositionF(x: int, y: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%d;%df" % (esc, y, x)

    class EraseScreen:
        @staticmethod
        def CursorToEnd() -> str:
            if disabled or _shutdown: return ""
            return "%s[0J" % esc

        @staticmethod
        def CursorToBegin() -> str:
            if disabled or _shutdown: return ""
            return "%s[1J" % esc

        @staticmethod
        def Entire() -> str:
            if disabled or _shutdown: return ""
            return "%s[2J" % esc

        @staticmethod
        def EntireBuffer() -> str:
            if disabled or _shutdown: return ""
            return "%s[3J" % esc

        @staticmethod
        def Clear(*_) -> str:
            if disabled or _shutdown: return ""
            return "%sc" % esc

    TermReset = Reset = EraseScreen().Clear

    class EraseLine:
        @staticmethod
        def CursorToEnd() -> str:
            if disabled or _shutdown: return ""
            return "%s[0K" % esc

        @staticmethod
        def CursorToBegin() -> str:
            if disabled or _shutdown: return ""
            return "%s[1K" % esc

        @staticmethod
        def Entire() -> str:
            if disabled or _shutdown: return ""
            return "%s[2K" % esc

    class Scroll:
        @staticmethod
        def Up(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dS" % (esc, n)

        @staticmethod
        def Down(n: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%dT" % (esc, n)

        @staticmethod
        def Entire() -> str:
            if disabled or _shutdown: return ""
            return "%s[r" % esc

        @staticmethod
        def StartEnd(start: int, end: int) -> str:
            if disabled or _shutdown: return ""
            return "%s[%d;%dr" % (esc, start, end)

    class Tab:
        @staticmethod
        def Set() -> str:
            if disabled or _shutdown: return ""
            return "%sH" % esc

        @staticmethod
        def Clear() -> str:
            if disabled or _shutdown: return ""
            return "%s[g" % esc

        @staticmethod
        def ClearAll() -> str:
            if disabled or _shutdown: return ""
            return "%s[3g" % esc

    class Printing:
        @staticmethod
        def Screen() -> str:
            if disabled or _shutdown: return ""
            return "%s[i" % esc

        @staticmethod
        def Line() -> str:
            if disabled or _shutdown: return ""
            return "%s[1i" % esc

        @staticmethod
        def AUXPortOn() -> str:
            if disabled or _shutdown: return ""
            return "%s[5i" % esc

        @staticmethod
        def AUXPortOff() -> str:
            if disabled or _shutdown: return ""
            return "%s[4i" % esc

    class DeviceStatus:
        @staticmethod
        def Code() -> str:
            if disabled or _shutdown: return ""
            return "%s[c" % esc  # -> <ESC>[{CODE}0c

        @staticmethod
        def Status() -> str:
            if disabled or _shutdown: return ""
            return "%s[5n" % esc  # -> <ESC>[0n = OK | <ESC>[3n = Failure

        @staticmethod
        def CursorPosition() -> str:
            if disabled or _shutdown: return ""
            return "%s[6n" % esc  # -> <ESC>[{ROW};{COLUMN}R

    class Cursor:
        @staticmethod
        def SavePosition() -> str:
            if disabled or _shutdown: return ""
            return "%s[s" % esc

        @staticmethod
        def RestorePosition() -> str:
            if disabled or _shutdown: return ""
            return "%s[u" % esc

        @staticmethod
        def Save() -> str:
            if disabled or _shutdown: return ""
            return "%s7" % esc

        @staticmethod
        def Restore() -> str:
            if disabled or _shutdown: return ""
            return "%s8" % esc

        @staticmethod
        def Hide() -> str:
            if disabled or _shutdown: return ""
            return "%s[?25l" % esc

        @staticmethod
        def Show() -> str:
            if disabled or _shutdown: return ""
            return "%s[?25h" % esc

    class Screen:
        @staticmethod
        def AlternateBufferOn() -> str:
            if disabled or _shutdown: return ""
            return "%s[?1049h" % esc

        @staticmethod
        def AlternateBufferOff() -> str:
            if disabled or _shutdown: return ""
            return "%s[?1049l" % esc

        @staticmethod
        def InvertOn() -> str:
            if disabled or _shutdown: return ""
            return "%s[?5h" % esc

        @staticmethod
        def InvertOff() -> str:
            if disabled or _shutdown: return ""
            return "%s[?5l" % esc

    def __init__(self, __esc: str = esc,
                 _disabled: bool = False,
                 raise_initerr: bool = True,
                 ignore_initerr: bool = True):

        global esc, disabled
        esc = __esc
        disabled = _disabled
        ansilib.InitWin32Ansi(raise_initerr, ignore_initerr)
        if not ansilib.CSInstance: ansilib.CSInstance = self

    @staticmethod
    def disable():
        global disabled
        disabled = True

    @staticmethod
    def enable():
        global disabled
        disabled = False

