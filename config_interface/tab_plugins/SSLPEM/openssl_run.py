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


from subprocess import Popen, PIPE
from threading import Thread
from config_interface.tab_plugins.SSLPEM import msg_strings


class _RunOpenSSL:
    def __init__(self, cmds: list, text_cell, flush=True):

        self.cmds = cmds
        self.exco = None
        self._processing = True
        self._text_cell = text_cell
        if flush:
            self._text_cell.delete()

        _cmd = self.cmds.pop(0)

        self._text_cell.insert(f': {_cmd} :\n\n')

        self._sp = Popen([_cmd],
                         shell=True,
                         stdin=-1,
                         stderr=PIPE,
                         stdout=PIPE
                         )

        Thread(target=self._text_insert_stderr, daemon=True).start()

        self._text_cell.text.after(3000, self._break)
        self._text_cell.text.after(3200, self._rec)

    def _text_insert_stderr(self):
        while self._processing:
            try:
                while err_ln := self._sp.stderr.readline():
                    self._text_cell.insert(err_ln.decode())
                self._text_cell.insert(self._sp.stdout.readline().decode())
            except Exception as e:
                return print(e)

    def _break(self):
        self._sp.communicate()
        self.exco = self._sp.returncode
        self._processing = False
        self._sp.kill()
        self._text_cell.insert(f'\n+++ exit {self.exco} +++\n\n')

    def _rec(self):
        if self.exco == 0 and self.cmds:
            _RunOpenSSL(self.cmds, self._text_cell, flush=False)


class _PrintOpenSSL:
    def __init__(self, cmds: list, text_cell):
        text_cell.top_insert(msg_strings.SEPARATOR128,
                             msg_strings.COMMAND_PRINT % tuple(cmds),
                             msg_strings.SEPARATOR128)


RunOpenSSL: _RunOpenSSL = _PrintOpenSSL

