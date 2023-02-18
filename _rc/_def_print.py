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


from sec.ansilib import *


class _NamedDict(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    def __getattr__(self, item):
        if self.__contains__(item):
            return self.__getitem__(item)
        return super(_NamedDict, self).__getattr__(item)


class ansi:

    def __init__(self, as_blueprint: bool = False):
        self.SGR = SelectGraphicRendition(_disabled=as_blueprint, raise_initerr=False, ignore_initerr=False)
        Colors.yellow_bg = Colors.bg("yellow2")
        Colors.yellow_fg = Colors.fg("orange2")
        self.CS = ControlSequence()
        self.print_timeout_bar = ("[▏  ]",
                                  "\b" * 7 + "[▎  ]",
                                  "\b" * 7 + "[▍  ]",
                                  "\b" * 7 + "[▌  ]",
                                  "\b" * 7 + "[▋  ]",
                                  "\b" * 7 + "[▊  ]",
                                  "\b" * 7 + "[▉  ]",
                                  "\b" * 7 + "[█  ]",
                                  "\b" * 7 + "[█▏ ]",
                                  "\b" * 7 + "[█▎ ]",
                                  "\b" * 7 + "[█▍ ]",
                                  "\b" * 7 + "[█▌ ]",
                                  "\b" * 7 + "[█▋ ]",
                                  "\b" * 7 + "[█▊ ]",
                                  "\b" * 7 + "[█▉ ]",
                                  "\b" * 7 + "[██▏]",
                                  "\b" * 7 + "[██▍]",
                                  "\b" * 7 + "[██▋]",
                                  "\b" * 7 + "[██▉]",
                                  "\b" * 7 + "[███]",)

        self.print_intervention_onoff = (self.CS.Screen.InvertOff(), self.CS.Screen.InvertOn())
        self.print_intervention_flush = [
            self.CS.Screen.InvertOff(),
            self.CS.Screen.InvertOn(),
            self.CS.Screen.InvertOff(),
            self.CS.Screen.InvertOn()
        ]
        self.print_intervention_error = self.SGR.wrap(" %s ", SGRAttr.bold, SGRAttr.invert)

        self.print_icos = _NamedDict(
            sharp="##",
            warn=self.SGR.wrap("[⚠ ]", SGRAttr.bold, Colors.yellow_bg, Colors.red_fg),
            tox="☣ ",
            x=self.SGR.wrap("[✕ ]", Colors.red_fg),
            y=self.SGR.wrap("🗸 ", Colors.green_fg),
            bridge_on="⎇ ",
            bridge_off="→ ",
            on="⏽ ",
            off="⏼ ",
            standby="⏻ ",
            shutdown="⓿ ",
            close="◯●",
            recycle="♽ ",
            broken_pipe="↛ ",
            i_pipe="↤ ",
            o_pipe="↦ ",
            kill="⌁⌁⌁",
            pings="···",
            listen="@@",
            key=self.SGR.wrap("🗝 ", SGRAttr.bold),
            exclam="!!",
            exclam2=self.SGR.wrap("!!", SGRAttr.bold, Colors.red_fg),
            quest="??",
            err=self.SGR.wrap("FAIL", Colors.red_fg),
            call=self.SGR.wrap("CALL", Colors.cyan_fg),
            cain=self.SGR.wrap("⛓ ", SGRAttr.bold),
            bind=self.SGR.wrap("⚯ ", SGRAttr.bold),
            stacks="⛁ ",
            wstacks=self.SGR.wrap("⛁ ", Colors.black_fg, Colors.white_bg),
            bstacks=self.SGR.wrap("⛁ ", Colors.black_bg, Colors.white_fg),
            lswush=self.SGR.wrap("⮨ ", Colors.cyan_fg, SGRAttr.bold),
            mail=self.SGR.wrap(" ✉ ", Colors.cyan_fg, SGRAttr.bold, SGRAttr.underline),
            interpro=self.SGR.wrap("⮒ ", Colors.fg("firebrick2")),
            intercon=self.SGR.wrap(" ⥆ ", Colors.fg("firebrick2"), SGRAttr.underline),
            drop=self.SGR.wrap("DROP", Colors.red_bg),
            rc=self.SGR.wrap("RC", SGRAttr.bold, Colors.yellow_bg),
        )

        # ifdef _noncall
        stream_format = {
            'fmt': "[%(asctime)-8s%(_ms)s] %(ansi_pr)s%(ansi_lv)-12s  (%(name)s) [%(ico)-2s] %(ansi_msg)s",
            'datefmt': "%H:%M:%S"}

        self.msgansis = _NamedDict(
            yellow=self.SGR.get(Colors.yellow_fg),
            red=self.SGR.get(Colors.red_fg),
            bold=self.SGR.get(SGRAttr.bold),
            underline=self.SGR.get(SGRAttr.underline)
        )

        level_to_ansi_prefix = {
            61: self.SGR.get(SGRAttr.bold, Colors.red_fg),
            60: self.SGR.get(Colors.red_fg),
            55: self.SGR.get(SGRAttr.bold, Colors.red_fg, Colors.yellow_bg),
            54: self.SGR.get(Colors.red_fg, Colors.yellow_bg),
            50: self.SGR.get(SGRAttr.bold, SGRAttr.underline, Colors.red_fg),
            45: self.SGR.get(SGRAttr.bold, Colors.red_fg),
            40: self.SGR.get(SGRAttr.bold, Colors.red_fg),
            35: self.SGR.get(SGRAttr.bold, Colors.yellow_fg),
            30: self.SGR.get(Colors.yellow_fg),
            25: self.SGR.get(SGRAttr.bold, Colors.cyan_fg),
            20: self.SGR.get(Colors.cyan_fg),
            15: '',
            10: '',
            5: '',
            0: ''
        }
        _r = self.SGR.get(SGRAttr.reset)
        level_to_ansi_name = {
            61: 'ALERT' + _r,
            60: 'FATAL' + _r,
            55: 'COUNTER' + _r,
            54: 'PREVENT' + _r,
            50: 'CRITICAL' + _r,
            45: 'DEPTHERR' + _r,
            40: 'ERROR' + _r,
            35: 'HARD' + _r,
            30: 'WARNING' + _r,
            25: 'INIT' + _r,
            20: 'INFO' + _r,
            15: 'DATA-I' + _r,
            10: 'DEBUG' + _r,
            5: 'DATA-O' + _r,
            0: 'NULL' + _r
        }
        # endif _noncall

        self.print_stream_args = (stream_format, self.msgansis, level_to_ansi_prefix, level_to_ansi_name)

        self.print_console_ansi = True


class ordin:

    def __init__(self):
        pass

    print_timeout_bar = (["·" for _ in range(20)])

    print_icos = _NamedDict(
        sharp="##",
        warn="W!",
        tox="TX",
        x="X!",
        y="**",
        bridge_on="|+",
        bridge_off="——",
        on=" 1",
        off=" 0",
        standby="-0",
        shutdown="00",
        close="00",
        recycle="wr",
        broken_pipe="\\-",
        i_pipe="<—",
        o_pipe="—>",
        kill="KILL",
        pings="···",
        listen="@@",
        key="++",
        exclam="!!",
        exclam2="!!",
        quest="??",
        err="FAIL",
        call="CALL",
        cain="++",
        drop="DROP",
        rc="RC",
        stacks="PH",
        wstacks="WH",
        bstacks="BL",
    )
    print_intervention_onoff = ('', '\n____?\n')
    print_intervention_flush = ['S', 'U', 'C', 'C', 'E', 'S', 'S', '!\n']
    print_intervention_error = '\n____ERROR: %s\n'

    # ifdef _noncall
    stream_format = {
        'fmt': "[%(asctime)-8s%(_ms)s] %(levelname)-8s  (%(name)s) [%(ico)-2s] %(message)s",
        'datefmt': "%H:%M:%S"}

    msgansis = _NamedDict()

    level_to_ansi_name = dict()
    level_to_ansi_prefix = dict()
    # endif _noncall

    print_stream_args = (stream_format, msgansis, level_to_ansi_prefix, level_to_ansi_name)

    print_console_ansi = False


class utf:

    def __init__(self):
        pass

    print_timeout_bar = ("[▏  ]",
                         "\b" * 7 + "[▎  ]",
                         "\b" * 7 + "[▍  ]",
                         "\b" * 7 + "[▌  ]",
                         "\b" * 7 + "[▋  ]",
                         "\b" * 7 + "[▊  ]",
                         "\b" * 7 + "[▉  ]",
                         "\b" * 7 + "[█  ]",
                         "\b" * 7 + "[█▏ ]",
                         "\b" * 7 + "[█▎ ]",
                         "\b" * 7 + "[█▍ ]",
                         "\b" * 7 + "[█▌ ]",
                         "\b" * 7 + "[█▋ ]",
                         "\b" * 7 + "[█▊ ]",
                         "\b" * 7 + "[█▉ ]",
                         "\b" * 7 + "[██▏]",
                         "\b" * 7 + "[██▍]",
                         "\b" * 7 + "[██▋]",
                         "\b" * 7 + "[██▉]",
                         "\b" * 7 + "[███]",)

    print_icos = _NamedDict(
        sharp="##",
        warn="[⚠ ]",
        tox="☣ ",
        x="[✕ ]",
        y="🗸 ",
        bridge_on="⎇ ",
        bridge_off="→ ",
        on="⏽ ",
        off="⏼ ",
        standby="⏻ ",
        shutdown="⓿ ",
        close="◯●",
        recycle="♽ ",
        broken_pipe="↛ ",
        i_pipe="↤ ",
        o_pipe="↦ ",
        kill="⌁⌁⌁",
        pings="···",
        listen="@@",
        key="🗝 ",
        exclam="!!",
        exclam2="!!",
        quest="??",
        err="FAIL",
        call="CALL",
        cain="⛓ ",
        drop="DROP",
        rc="RC",
        stacks="⛁ ",
        wstacks="⛁ ",
        bstacks="⛁ "
    )
    print_intervention_onoff = ('', '\n____?\n')
    print_intervention_flush = ['S', 'U', 'C', 'C', 'E', 'S', 'S', '!\n']
    print_intervention_error = '\n____ERROR: %s\n'

    # ifdef _noncall
    stream_format = {
        'fmt': "[%(asctime)-8s%(_ms)s] %(levelname)-8s  (%(name)s) [%(ico)-2s] %(message)s",
        'datefmt': "%H:%M:%S"}

    msgansis = _NamedDict()

    level_to_ansi_name = dict()
    level_to_ansi_prefix = dict()
    # endif _noncall

    print_stream_args = (stream_format, msgansis, level_to_ansi_prefix, level_to_ansi_name)

    print_console_ansi = False


_base = ansi(True)

for __attr in ('msgansis', 'print_icos'):
    for _attr in getattr(_base, __attr):
        getattr(utf, __attr).setdefault(_attr, '')
        getattr(ordin, __attr).setdefault(_attr, '')
