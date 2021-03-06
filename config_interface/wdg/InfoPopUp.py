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


from tkinter import Menu
from tkinter import RIGHT, DISABLED

class InfoPopUp(Menu):
    def __init__(self,
                 target,
                 info_lines: iter,
                 pop_pos: tuple[int, int] = (10, 10),
                 timers: tuple[int, int, int] = (2000, 500, 200),
                 foreground: str = '#000000',
                 background: str = '#FFFFFF',
                 font=('Consolas', 7),
                 pre_pop_call: ... = None
                 ):

        """
        Tk-popup-menu to function as info-/disclaimer-popup.

        info_lines = [
        str,  ............> line
        str,  ............> line
        None,  .......> ------------------
        str  .............> line
        ]

        :param target: the target widget
        :param info_lines: [line: str, separator: None]
        :param pop_pos: x/y adjustment
        :param timers: ms (popup, close, clear)
        :param foreground: info-popup foreground (-> Menu.disabledforeground)
        :param background: info-popup background
        :param font: tk font
        :param pre_pop_call: called before popup
        """

        self.pop_pos = pop_pos[0], pop_pos[1]
        self.popup_timer, self.unpost_timer, self.clear_timer = timers

        self.pre_pop_call = (pre_pop_call if pre_pop_call else lambda: None)

        Menu.__init__(self,
                      target,
                      tearoff=0,
                      disabledforeground=foreground, activeforeground=foreground,
                      activebackground=background,
                      bg=background,
                      bd=0, activeborderwidth=0
                      )

        for _line in info_lines:
            if _line is None:
                self.add_separator()
            else:
                self.add_command(
                    label=_line,
                    compound=RIGHT,
                    font=font,
                    state=DISABLED
                )

        target.bind("<Enter>", self._popup)
        target.bind("<Leave>", self._clear)
        target.bind("<Button>", lambda _: self.unpost())
        self.bind("<Enter>", lambda _: self.focus.__setitem__(1, True))
        self.bind("<Leave>", self._upost)
        self.focus = [False, False]
        self.posted = False

    def _suppress(self, _):
        self.focus = [False, False]
        self.posted = False

    def _clear(self, _):
        self.focus[0] = False

        def clear():
            if True not in self.focus:
                self.unpost()
                self.posted = False

        self.after(self.clear_timer, clear)

    def _popup(self, _):
        self.focus[0] = True
        if self.posted: return

        def popup():
            if not self.focus[0]: return
            self.pre_pop_call()
            wf = self.focus_get()
            try:
                self.tk_popup(
                    self.winfo_pointerx() + self.pop_pos[0],
                    self.winfo_pointery() + self.pop_pos[1])
            finally:
                if wf: wf.focus_force()
                self.grab_release()
                self.posted = True

        self.after(self.popup_timer, popup)

    def _upost(self, _):
        self.focus[1] = False
        if True in self.focus: return

        def upost():
            try:
                self.unpost()
            finally:
                self.posted = False

        self.after(self.unpost_timer, upost)
