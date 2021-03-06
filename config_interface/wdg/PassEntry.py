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

from tkinter import Entry
from tkinter import END, INSERT, SEL_FIRST, SEL_LAST
from sys import platform


class PassEntry(Entry):

    def __init__(self,
                 master,
                 show: chr="*",
                 delay: int = 800,
                 getpass_range: tuple = None,
                 getpass_call: ... = None,
                 getpass_del: bool = False,
                 **tk_kwargs,
                 ):

        """
        Password entry with time-delay hiding.
        Alternative to `Entry(master, show="*")'

        get password:
            - protected member: `self._password'
            - call `self.getpass': args `getpass_*' executed here
            - call `self.get': args `getpass_*' executed here

        :param master: root tk
        :param show: displayed char
        :param delay: hiding delay
        :param getpass_range: assert password length
        :param getpass_call: callable, gets `self.password' as argument
        :param getpass_del: delete `self.password' and flush entry if True
        :param tk_kwargs: Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, highlightbackground,
        highlightcolor, highlightthickness, insertbackground,
        insertborderwidth, insertofftime, insertontime, insertwidth,
        invalidcommand, invcmd, justify, relief, selectbackground,
        selectborderwidth, selectforeground, state, takefocus,
        textvariable, validate, validatecommand, vcmd, width,
        xscrollcommand.
        """
        
        self._password: str = ""

        self.delay: int = delay
        self.show: chr = show

        self.getpass_range: tuple = getpass_range
        self.getpass_call: ... = getpass_call
        self.getpass_del: bool = getpass_del

        Entry.__init__(self, master, tk_kwargs)
        self.bind("<Key>", self._run)
        self.bind("<Button>", self._run)
        
        self._external: bool = False

        self.get = self.getpass

        if platform == "linux":
            self._states = (0, 16, 17, 144, 145)
        elif platform == "win32":
            self._states = (0, 8, 9)

    def _char(self, event) -> str:
        def del_mkey():
            i = self.index(INSERT)
            self._delete(i - 1, i)
        if event.keysym in ('Delete', 'BackSpace'):
            return ""
        elif event.keysym == "Multi_key" and len(event.char) == 2:
            if event.char[0] == event.char[1]:
                self.after(10, del_mkey)
                return event.char[0]
            return event.char
        elif event.char != '\\' and '\\' in f"{event.char=}":
            return ""
        elif event.num in (1, 2, 3):
            return ""
        elif event.state in self._states:
            return event.char
        return ""

    def _get(self):
        return self.tk.call(self._w, 'get')
        
    def _delete(self, first, last=None):
        self.tk.call(self._w, 'delete', first, last)

    def _insert(self, index, string: str) -> None:
        self.tk.call(self._w, 'insert', index, string)
        
    def _run(self, event):

        if self._external and self._char(event):
            self._external = False
            self.clear()

        def hide(index: int, lchar: int):
            i = self.index(INSERT)
            for j in range(lchar):
                self._delete(index + j, index + 1 + j)
                self._insert(index + j, self.show)
            self.icursor(i)

        if event.keysym == 'Delete':
            if self.select_present():
                start = self.index(SEL_FIRST)
                end = self.index(SEL_LAST)
            else:
                start = self.index(INSERT)
                end = start + 1

            self._password = self._password[:start] + self._password[end:]

        elif event.keysym == 'BackSpace':
            if self.select_present():
                start = self.index(SEL_FIRST)
                end = self.index(SEL_LAST)
            else:
                if not (start := self.index(INSERT)):
                    return
                end = start
                start -= 1

            self._password = self._password[:start] + self._password[end:]

        elif char := self._char(event):
            if self.select_present():
                start = self.index(SEL_FIRST)
                end = self.index(SEL_LAST)
            else:
                start = self.index(INSERT)
                end = start

            self._password = self._password[:start] + char + self._password[end:]

            self.after(self.delay, hide, start, len(char))

    def insert(self, index, string: str) -> None:
        self._external = True
        self.tk.call(self._w, 'insert', index, string)
        
    def delete(self, first, last=None) -> None:
        self._external = True
        self.tk.call(self._w, 'delete', first, last)
        
    def clear(self):
        del self._password
        self._password = ""
        self._delete(0, END)

    def getpass(self):
        password = self._password
        if self.getpass_range:
            assert len(self._password) in range(*self.getpass_range), f'## Password not in range{self.getpass_range}'
        if self.getpass_call:
            password = self.getpass_call.__call__(self._password)
        if self.getpass_del:
            del self._password
            self._password = ""
            self._delete(0, END)
        return password
