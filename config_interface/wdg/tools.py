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


from tkinter import Menu, Text
from tkinter import LEFT, END
from re import Pattern, search, finditer


class MenuCascade(Menu):

    def __init__(self,
                 master: Menu,
                 casctop_label: str,
                 labels: [list, tuple],
                 commands: [list, tuple],
                 i_is_radio: [list, tuple] = (),
                 i_is_check: [list, tuple] = (),
                 casctop_kwargs: dict=None,
                 casc_kwargs: dict=None,
                 button_kwargs: dict=None,
                 radio_kwargs: dict=None,
                 check_kwargs: dict=None
                 ):

        if casctop_kwargs is None: casctop_kwargs = {}
        if casc_kwargs is None: casc_kwargs = {}
        if button_kwargs is None: button_kwargs = {}
        if radio_kwargs is None: radio_kwargs = {}
        if check_kwargs is None: check_kwargs = {}

        Menu.__init__(self,
                      master,
                      tearoff=0,
                      **casc_kwargs)
        master.add_cascade(
            label=casctop_label,
            menu=self,
            **casctop_kwargs
        )

        for i in range(len(labels)):
            if i in i_is_check:
                self.add_checkbutton(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **check_kwargs
                )
            elif i in i_is_radio:
                self.add_radiobutton(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **radio_kwargs
                )
            elif labels[i] is None:
                self.add_separator()
            else:
                self.add_command(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **button_kwargs
                )


class PopUpMenu(Menu):
    def __init__(self,
                 master,
                 labels: [list, tuple],
                 commands: [list, tuple],
                 bind_up: [list, tuple],
                 i_is_radio: [list, tuple] = (),
                 i_is_check: [list, tuple] = (),
                 button_kwargs: dict = None,
                 radio_kwargs: dict = None,
                 check_kwargs: dict = None
                 ):

        if button_kwargs is None: button_kwargs = {}
        if radio_kwargs is None: radio_kwargs = {}
        if check_kwargs is None: check_kwargs = {}

        Menu.__init__(self, master, tearoff=0)

        for i in range(len(labels)):
            if i in i_is_check:
                self.add_checkbutton(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **check_kwargs
                )
            elif i in i_is_radio:
                self.add_radiobutton(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **radio_kwargs
                )
            elif labels[i] is None:
                self.add_separator()
            else:
                self.add_command(
                    label=labels[i],
                    command=commands[i],
                    compound=LEFT,
                    **button_kwargs
                )

        for up in bind_up:
            up.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class TextHighlighting:
    def __init__(self,
                 text:Text,
                 main_config: dict[Pattern]=False,
                 first_clause: dict[Pattern]=False,
                 sub_loop: list[dict[Pattern], set[Pattern], dict[Pattern]]=False,
                 strict_sub_loop: list[dict[Pattern], set[Pattern], dict[Pattern]]=False,
                 at_call: dict[Pattern]=None,
                 ):

        self.text = text
        self.config: dict[Pattern] = (main_config if main_config else {})
        self.first_clause: dict[Pattern] = first_clause
        self.sub_loop: list[dict[Pattern], set[Pattern], dict[Pattern]] = (sub_loop if sub_loop else [{}, set(), {}])
        self.strict_sub_loop: list[dict[Pattern], set[Pattern], dict[Pattern]] = (strict_sub_loop if strict_sub_loop else [{}, set(), {}])
        self.at_call = (at_call if at_call else {})

        self.alltags: set = set()
        self.sub_tags: dict[str, set] = dict()
        self.ssub_tags: dict[str, set] = dict()

        self._read_start = "1.0"

    def _add_tag(self, _lineno, _match, _kwarg):
        start = "%d.%d" % (_lineno, _match.start())
        end = "%d.%d" % (_lineno, _match.end())
        _id = "%s:%s::%s" % (start, end, _match.group())
        self.text.tag_add(_id, start, end)
        self.text.tag_config(_id, **_kwarg)
        return _id

    def highlight(self, flush=False):

        if flush and self.alltags:
            self.text.tag_delete(*self.alltags)
            self.alltags: set = set()
            self.sub_tags: dict[str, set] = dict()
            self.ssub_tags: dict[str, set] = dict()

        first_clause = (self.first_clause if self._read_start == "1.0" else False)
        inside_sub_loop = False
        inside_ssub_loop = False

        _start = self._read_start
        self._read_start = "1.0"

        for n, ln in enumerate(self.text.get(_start, END).splitlines(), int(search("\d+", _start).group())):
            if first_clause:
                _config = self.first_clause
            else:
                _config = self.config

            try:
                for p in self.at_call:
                    if m := search(p, ln):
                        self.at_call[p].__call__(ln, n, m)
            except RuntimeError:
                for p in self.at_call:
                    if m := search(p, ln):
                        self.at_call[p].__call__(ln, n, m)

            if not inside_sub_loop:
                for p in self.sub_loop[0]:
                    for m in finditer(p, ln):
                        _id = self._add_tag(n, m, self.sub_loop[0][p])
                        self.alltags.add(_id)
                        self.sub_tags[_id] = set()
                        inside_sub_loop = _id

            else:
                for p in self.sub_loop[1]:
                    if search(p, ln):
                        self._read_start = "%d.0" % n
                        return self.highlight(False)

                if inside_sub_loop:
                    for p in self.sub_loop[2]:
                        for m in finditer(p, ln):
                            _id = self._add_tag(n, m, self.sub_loop[2][p])
                            self.alltags.add(_id)
                            self.sub_tags[inside_sub_loop].add(_id)

            if not inside_ssub_loop:
                for p in self.strict_sub_loop[0]:
                    for m in finditer(p, ln):
                        _id = self._add_tag(n, m, self.strict_sub_loop[0][p])
                        self.alltags.add(_id)
                        self.ssub_tags[_id] = set()
                        inside_ssub_loop = _id

                if inside_ssub_loop:
                    continue

            else:
                for p in self.strict_sub_loop[1]:
                    if search(p, ln):
                        self._read_start = "%d.0" % n
                        return self.highlight(False)

                if inside_ssub_loop:
                    for p in self.strict_sub_loop[2]:
                        for m in finditer(p, ln):
                            _id = self._add_tag(n, m, self.strict_sub_loop[2][p])
                            self.alltags.add(_id)
                            self.ssub_tags[inside_ssub_loop].add(_id)
                    continue

            for p in _config:
                for m in finditer(p, ln):
                    first_clause = False
                    _id = self._add_tag(n, m, _config[p])
                    self.alltags.add(_id)

