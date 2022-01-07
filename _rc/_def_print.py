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

class ansi:
    print_timeout_bar = ("\x1b[s[▏  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▎  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▍  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▌  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▋  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▊  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[▉  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█  ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▏ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▎ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▍ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▌ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▋ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▊ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[█▉ ]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[██▏]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[██▍]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[██▋]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[██▉]\x1b[1B\x1b[5D",
                         '\b'*5+"\x1b[u[███]\x1b[1B\x1b[5D",)

    class print_icos:
        sharp = "##"
        warn = "\x1b[43;1;31m[⚠ ]\x1b[0m"
        tox = "☣ "
        x = "\x1b[31m[✕ ]\x1b[0m"
        y = "\x1b[1;32m🗸 \x1b[0m"
        bridge_on = "⎇ "
        bridge_off = "→ "
        on = "⏽ "
        off = "⏼ "
        standby = "⏻ "
        shutdown = "⓿ "
        close = "◯●"
        recycle = "♽ "
        broken_pipe = "↛ "
        i_pipe = "↤ "
        o_pipe = "↦ "
        kill = "⌁⌁⌁"
        pings = "···"
        listen = "@@"
        key = "\x1b[1m🗝 \x1b[0m"
        exclam = "!!"
        exclam2 = "\x1b[1;31m!!\x1b[0m"
        quest = "??"
        err = "\x1b[31mFAIL\x1b[0m"
        call = "\x1b[46mCALL\x1b[0m"
        cain = "\x1b[1m⛓ \x1b[0m"
        bind = "\x1b[1m⚯ \x1b[0m"
        stacks = "⛁ "
        wstacks = "\x1b[30;47m⛁ \x1b[0m"
        bstacks = "\x1b[37;40m⛁ \x1b[0m"
        lswush = "\x1b[1;36m⮨ \x1b[0m"
        mail = "\x1b[1;4;36m ✉ \x1b[0m"
        interpro = "\x1b[91m⮒ \x1b[0m"
        intercon = "\x1b[4;91m ⥆ \x1b[0m"
        drop = "\x1b[41mDROP\x1b[0m"
        rc = "\x1b[1;43mRC\x1b[0m"

    print_intervention_onoff = ('\x1b[?5l', '\x1b[?5h')
    print_intervention_flush = ['\x1b[?5l', '\x1b[?5h', '\x1b[?5l', '\x1b[?5h']
    print_intervention_error = '\x1b[7;1m %s \x1b[0m'

    # ifdef _noncall
    stream_format = {
        'fmt': "[%(asctime)-8s%(_ms)s] %(ansi_pr)s%(ansi_lv)-12s  (%(name)s) [%(ico)-2s] %(ansi_msg)s",
        'datefmt': "%H:%M:%S"}

    class msgansis:
        yellow = '\x1b[33m'
        red = '\x1b[31m'
        bold = '\x1b[1m'
        underline = '\x1b[4m'

    level_to_ansi_prefix = {
        61: '\x1b[1;31m',
        60: '\x1b[31m',
        55: '\x1b[43;1;31m',
        54: '\x1b[43;31m',
        50: '\x1b[4;1;31m',
        45: '\x1b[1;31m',
        40: '\x1b[1;31m',
        35: '\x1b[1;33m',
        30: '\x1b[33m',
        25: '\x1b[1;36m',
        20: '\x1b[36m',
        15: '',
        10: '',
        5: '',
        0: ''
    }
    level_to_ansi_name = {
        61: 'ALERT\x1b[0m',
        60: 'FATAL\x1b[0m',
        55: 'COUNTER\x1b[0m',
        54: 'PREVENT\x1b[0m',
        50: 'CRITICAL\x1b[0m',
        45: 'DEPTHERR\x1b[0m',
        40: 'ERROR\x1b[0m',
        35: 'HARD\x1b[0m',
        30: 'WARNING\x1b[0m',
        25: 'INIT\x1b[0m',
        20: 'INFO\x1b[0m',
        15: 'DATA-I\x1b[0m',
        10: 'DEBUG\x1b[0m',
        5: 'DATA-O\x1b[0m',
        0: 'NULL\x1b[0m'
    }
    # endif _noncall

    print_stream_args = (stream_format, msgansis, level_to_ansi_prefix, level_to_ansi_name)

class ordin:

    print_timeout_bar = (["·" for _ in range(20)])

    class print_icos:
        sharp = "##"
        warn = "W!"
        tox = "TX"
        x = "X!"
        y = "**"
        bridge_on = "|+"
        bridge_off = "——"
        on = " 1"
        off = " 0"
        standby = "-0"
        shutdown = "00"
        close = "00"
        recycle = "wr"
        broken_pipe = "\\-"
        i_pipe = "<—"
        o_pipe = "—>"
        kill = "KILL"
        pings = "···"
        listen = "@@"
        key = "++"
        exclam = "!!"
        exclam2 = "!!"
        quest = "??"
        err = "FAIL"
        call = "CALL"
        cain = "++"
        drop = "DROP"
        rc = "RC"
        stacks = "PH"
        wstacks = "WH"
        bstacks = "BL"

    print_intervention_onoff = ('', '\n____?\n')
    print_intervention_flush = ['S', 'U', 'C', 'C', 'E', 'S', 'S', '!\n']
    print_intervention_error = '\n____ERROR: %s\n'

    # ifdef _noncall
    stream_format = {
            'fmt': "[%(asctime)-8s%(_ms)s] %(levelname)-8s  (%(name)s) [%(ico)-2s] %(message)s",
            'datefmt': "%H:%M:%S"}
    class msgansis:
        pass
    level_to_ansi_name = dict()
    level_to_ansi_prefix = dict()
    # endif _noncall

    print_stream_args = (stream_format, msgansis, level_to_ansi_prefix, level_to_ansi_name)

class utf:
    print_timeout_bar = ("[▏  ]",
                         "\b\b\b\b\b[▎  ]",
                         "\b\b\b\b\b[▍  ]",
                         "\b\b\b\b\b[▌  ]",
                         "\b\b\b\b\b[▋  ]",
                         "\b\b\b\b\b[▊  ]",
                         "\b\b\b\b\b[▉  ]",
                         "\b\b\b\b\b[█  ]",
                         "\b\b\b\b\b[█▏ ]",
                         "\b\b\b\b\b[█▎ ]",
                         "\b\b\b\b\b[█▍ ]",
                         "\b\b\b\b\b[█▌ ]",
                         "\b\b\b\b\b[█▋ ]",
                         "\b\b\b\b\b[█▊ ]",
                         "\b\b\b\b\b[█▉ ]",
                         "\b\b\b\b\b[██▏]",
                         "\b\b\b\b\b[██▍]",
                         "\b\b\b\b\b[██▋]",
                         "\b\b\b\b\b[██▉]",
                         "\b\b\b\b\b[███]",)

    class print_icos:
        sharp = "##"
        warn = "[⚠ ]"
        tox = "☣ "
        x = "[✕ ]"
        y = "🗸 "
        bridge_on = "⎇ "
        bridge_off = "→ "
        on = "⏽ "
        off = "⏼ "
        standby = "⏻ "
        shutdown = "⓿ "
        close = "◯●"
        recycle = "♽ "
        broken_pipe = "↛ "
        i_pipe = "↤ "
        o_pipe = "↦ "
        kill = "⌁⌁⌁"
        pings = "···"
        listen = "@@"
        key = "🗝 "
        exclam = "!!"
        exclam2 = "!!"
        quest = "??"
        err = "FAIL"
        call = "CALL"
        cain = "⛓ "
        drop = "DROP"
        rc = "RC"
        stacks = "⛁ "
        wstacks = "⛁ "
        bstacks = "⛁ "

    print_intervention_onoff = ('', '\n____?\n')
    print_intervention_flush = ['S', 'U', 'C', 'C', 'E', 'S', 'S', '!\n']
    print_intervention_error = '\n____ERROR: %s\n'

    # ifdef _noncall
    stream_format = {
        'fmt': "[%(asctime)-8s%(_ms)s] %(levelname)-8s  (%(name)s) [%(ico)-2s] %(message)s",
        'datefmt': "%H:%M:%S"}

    class msgansis:
        pass

    level_to_ansi_name = dict()
    level_to_ansi_prefix = dict()
    # endif _noncall

    print_stream_args = (stream_format, msgansis, level_to_ansi_prefix, level_to_ansi_name)


for _attr in list(ansi.msgansis.__dict__):
    if _attr.startswith('__'): continue
    setattr(utf.msgansis, _attr, '')
    setattr(ordin.msgansis, _attr, '')

for _attr in list(ansi.print_icos.__dict__):
    if _attr.startswith('__'): continue
    if not hasattr(utf.print_icos, _attr):
        setattr(utf.print_icos, _attr, '')
    if not hasattr(ordin.print_icos, _attr):
        setattr(ordin.print_icos, _attr, '')

for _attr in list(ansi.__dict__):
    if _attr.startswith('__'): continue
    if not hasattr(utf.print_icos, _attr):
        setattr(utf.print_icos, _attr, '')
    if not hasattr(ordin.print_icos, _attr):
        setattr(ordin.print_icos, _attr, '')
