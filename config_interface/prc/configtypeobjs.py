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

from tkinter import Label, Button, Entry, END, E, W, IntVar, Radiobutton, Tk, Checkbutton
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename

from os import path, access, devnull
from re import search, compile
from sys import platform, getfilesystemencoding
from hashlib import sha224, sha256, sha512

from config_interface.sec.auto_close import widget_close
from config_interface.wdg.PassEntry import PassEntry
from config_interface._rc import _run as CRC

GridKwargs = {
    'row': 0,
    'column': 1,
    'columnspan': 1,
    'sticky': E
}

class BaseMethods:
    class entry:
        def get(self): return f"{self}"

    def __init__(self, configKey, txt_cell):
        self.txt_cell = txt_cell
        if not txt_cell:
            self.txt_cell = self
        self.entry = self.entry()
        self.configKey = configKey
        for _v in ("val", "see", "cnf"):
            if not hasattr(self, _v):
                setattr(self, _v, f"[i] {self}<{_v=}>")

        self.all_wg: tuple = tuple()

    def insert(self, *args, **kwargs):
        print(f"{str().join([str(_s) + ' ' for _s in args])}{kwargs} @ {self.insert.__qualname__!r}")

    def fill(self, val):
        if self.val is not None: return
        CRC.strings[self.configKey].label_disabled, CRC.strings[self.configKey].label_none = CRC.strings[
                                                                                                 self.configKey].label_none, \
                                                                                             CRC.strings[
                                                                                                 self.configKey].label_disabled
        self.setval(val)
        CRC.strings[self.configKey].label_none, CRC.strings[self.configKey].label_disabled = CRC.strings[
                                                                                                 self.configKey].label_disabled, \
                                                                                             CRC.strings[
                                                                                                 self.configKey].label_none

    def setnone(self):
        self.setval(None)

    def get(self):
        self.setval(self.entry.get().strip())
        return self.cnf

    def del_insert(self, entry, cont):
        entry.delete(0, END)
        entry.insert(0, cont)

    def set_color(self, widgets: tuple, bg: tuple, fg: tuple):
        for widget, bg, fg in zip(widgets, bg, fg):
            widget.config(bg=bg, fg=fg)

    def setval(self, *args, **kwargs):
        print(f"[i] {self.setval.__qualname__!r}")

    def _expand_all_wg(self, __wg):
        if not isinstance(__wg, tuple):
            __wg = (__wg,)
        self.all_wg += __wg


class ButtonEntryBase(BaseMethods):
    def __init__(self, master, configKey, txt_cell, btn_tx, btn_cmd, btn_tx2=None, btn_cmd2=None, **grid_kwargs):
        """
        [button][  entry  ] (columns = 2, 3)
        [button][button][  entry  ] (columns = 1, 2, 3)

        :param master: master widget
        :param btn_tx: button text
        :param btn_cmd: button command
        :param btn_tx2: button text
        :param btn_cmd2: button command
        :return: widgets: button, entry | button, button2, entry
        """
        BaseMethods.__init__(self, configKey, txt_cell)

        self._container = Label(master,
                                height=CRC.geo[self.configKey].btn_ent_height)

        self._expand_all_wg(self._container)

        self.button_kw = {
            'master': self._container,
            'bd': CRC.configs[self.configKey].btn_ent_button_bd,
            'font': CRC.fonts[self.configKey].main_font_bold,
            'padx': CRC.configs[self.configKey].btn_ent_button_padx,
            'pady': CRC.configs[self.configKey].btn_ent_button_pady,
            'relief': CRC.configs[self.configKey].btn_ent_button_relief
        }
        self.entry_kw = {
            'master': self._container,
            'width': CRC.geo[self.configKey].btn_ent_entry_width,
            'relief': CRC.configs[self.configKey].btn_ent_entry_relief,
            'highlightthickness': CRC.configs[self.configKey].btn_ent_entry_hilith,
            'font': CRC.fonts[self.configKey].main_font
        }

        self.button = Button(text=btn_tx,
                             image=CRC.fonts[self.configKey].ico_btn1_ent,
                             command=btn_cmd,
                             **self.button_kw)
        self.button.grid(column=2, row=0, sticky=E)

        self._expand_all_wg(self.button)

        if btn_tx2 is not None:
            self.button2 = Button(text=btn_tx2,
                                  image=CRC.fonts[self.configKey].ico_btn2_ent,
                                  command=btn_cmd2,
                                  **self.button_kw)
            self.button2.grid(column=1, row=0, sticky=E)
            self._expand_all_wg(self.button2)
        self.entry = Entry(**self.entry_kw)
        self.entry.grid(column=3, row=0, sticky=E)
        self._container.grid(**GridKwargs | grid_kwargs)
        self.entry.bind("<Tab>", lambda _: self.get())
        self.entry.bind(CRC.SHIFT_TAB, lambda _: self.get())
        self._expand_all_wg(self.entry)


class EntryBase(BaseMethods):
    def __init__(self, master, configKey, txt_cell, width, **grid_kwargs):
        """
        [  entry  ] (column=1)

        :param master: master widget
        :param width: entry width
        :return: widget: entry
        """
        BaseMethods.__init__(self, configKey, txt_cell)

        self.entry = Entry(master,
                           font=CRC.fonts[self.configKey].main_font,
                           width=width,
                           relief=CRC.configs[self.configKey].ent_entry_relief,
                           highlightthickness=CRC.configs[self.configKey].ent_entry_hilith)
        self.entry.grid(**GridKwargs | grid_kwargs)
        self.entry.bind("<Tab>", lambda _: self.get())
        self.entry.bind(CRC.SHIFT_TAB, lambda _: self.get())
        self._expand_all_wg(self.entry)


class PassEntryBase(BaseMethods):
    def __init__(self, master, configKey, txt_cell, width, **grid_kwargs):
        """
        [  entry  ] (column=1)

        :param master: master widget
        :param width: entry width
        :return: widget passentry
        """
        BaseMethods.__init__(self, configKey, txt_cell)

        self.entry = PassEntry(master,
                               font=CRC.fonts[self.configKey].main_font,
                               width=width,
                               relief=CRC.configs[self.configKey].ent_entry_relief,
                               highlightthickness=CRC.configs[self.configKey].ent_entry_hilith)
        self.entry.grid(**GridKwargs | grid_kwargs)
        self.entry.bind("<Tab>", lambda _: self.get())
        self.entry.bind(CRC.SHIFT_TAB, lambda _: self.get())
        self._expand_all_wg(self.entry)


class LabelEntryBase(BaseMethods):
    def __init__(self, master, configKey, txt_cell, *tx, ent_width, **grid_kwargs):
        """
        [label][ entry ]... for label in *tx (start_column=1)

        :param master: master widget
        :param tx: label texts
        :param ent_width: entry width
        :return: list(label widgets), list(entry widgets)
        """
        BaseMethods.__init__(self, configKey, txt_cell)

        self._container = Label(master,
                                height=CRC.geo[self.configKey].lbl_ent_height)

        self._expand_all_wg(self._container)

        self.labels, self.entrys = [], []
        for text, column in zip(tx, range(1, len(tx) * 2 + 1, 2)):
            self.labels.append(
                Label(self._container,
                      font=CRC.fonts[self.configKey].main_font,
                      text=text,
                      height=CRC.geo[self.configKey].lbl_ent_label_height,
                      relief=CRC.configs[self.configKey].lbl_ent_label_relief)
            )
            self.labels[-1].grid(column=column, row=0, sticky=E)
            self.entrys.append(
                Entry(self._container,
                      font=CRC.fonts[self.configKey].main_font_bold,
                      width=ent_width,
                      relief=CRC.configs[self.configKey].lbl_ent_entry_relief)
            )
            self.entrys[-1].grid(column=column + 1, row=0, sticky=E)
            self.entrys[-1].bind("<Tab>", lambda _: self.get())
            self.entrys[-1].bind(CRC.SHIFT_TAB, lambda _: self.get())
        self._container.grid(**GridKwargs | grid_kwargs)

        self._expand_all_wg(tuple(self.labels) + tuple(self.entrys))


class type_pass(PassEntryBase):
    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        PassEntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_pass, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = {
            'sha224': lambda _s: sha224(_s.encode('utf8')).hexdigest(),
            'sha256': lambda _s: sha256(_s.encode('utf8')).hexdigest(),
            'sha512': lambda _s: sha512(_s.encode('utf8')).hexdigest(),
            'sha0': lambda _s: _s,
            '0': lambda _s: _s
        }.get(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['pass'], cnf_ln).group()
        )

    def get(self):
        if (pw := self.entry.get()) == "":
            return self.cnf
        self.setval(pw)
        return self.cnf

    def setval(self, value):
        if value is None:
            self.entry.clear()
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif isinstance(value, str) and value.strip() == "":
            self.entry.clear()
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_str
        elif str(value).lower() == "false":
            self.entry.clear()
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        else:
            self.val, self.cnf = value, self.type_cnf(value)
            self.see = CRC.strings[self.configKey].label_hashed
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_pass_entry_bg,),
                       (CRC.colors[self.configKey].color_pass_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_pass_entry_bg',),
                                               ('color_pass_entry_fg',), setmeth)


class type_dir(ButtonEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        ButtonEntryBase.__init__(self, container, configKey, txt_cell, " + ", lambda: self.setval(askdirectory()),
                                 **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = int(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['dir'], cnf_ln).group()
        )

    def setval(self, value):
        if value and value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_dir_entry_bg)
        if value == () or value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif isinstance(value, str) and not value.strip():
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_pwd
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif access(search(CRC.PATH_RE, (value := path.realpath(value))).group(), self.type_cnf) and path.isdir(value):
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_notfound)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.button, self.entry),
                       (CRC.colors[self.configKey].color_dir_button_bg, CRC.colors[self.configKey].color_dir_entry_bg),
                       (CRC.colors[self.configKey].color_dir_button_fg, CRC.colors[self.configKey].color_dir_entry_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.button, self.entry),
                                               ('color_dir_button_bg', 'color_dir_entry_bg'),
                                               ('color_dir_button_fg', 'color_dir_entry_fg'), setmeth)


class type_str(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell=None, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_str, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname

    def setval(self, value):
        if value == self.see: return
        if value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif isinstance(value, str) and value.strip() == "":
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_str
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        else:
            self.val, self.cnf = value, value
            self.see = value
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_str_entry_bg,),
                       (CRC.colors[self.configKey].color_str_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_str_entry_bg',),
                                               ('color_str_entry_fg',), setmeth)


class type_point(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell=None, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_point, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = compile(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['point'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_point_entry_bg)
        if value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif isinstance(value, float):
            self.val, self.cnf = value, value
            self.see = str(value)
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif not search(self.type_cnf, value):
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_point)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        else:
            self.val, self.cnf = float(value), float(value)
            self.see = value
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_point_entry_bg,),
                       (CRC.colors[self.configKey].color_point_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_point_entry_bg',),
                                               ('color_point_entry_fg',), setmeth)


class type_codec(EntryBase):

    system = getfilesystemencoding()

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell=None, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_codec, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_codec_entry_bg)
        if value is None:
            self.val, self.cnf = self.system, self.system
            self.see = self.system
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        else:
            try:
                str().encode(value)
                self.val, self.cnf = value, value
                self.see = value
            except LookupError:
                self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_codec)
                self.val, self.cnf = None, None
                self.see = value
                self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_codec_entry_bg,),
                       (CRC.colors[self.configKey].color_codec_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_codec_entry_bg',),
                                               ('color_codec_entry_fg',), setmeth)


class type_int(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_int, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = compile(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['int'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_int_entry_bg)
        if value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif isinstance(value, int):
            self.val, self.cnf = value, value
            self.see = str(value)
        elif not search(self.type_cnf, value):
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_int)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        else:
            self.val, self.cnf = int(value), int(value)
            self.see = value
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_int_entry_bg,),
                       (CRC.colors[self.configKey].color_int_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_int_entry_bg',),
                                               ('color_int_entry_fg',), setmeth)


class type_choice(BaseMethods):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        BaseMethods.__init__(self, configKey, txt_cell)
        self.varname = varname
        self.val = None
        self.see = None
        self.cnf = None
        self.btns_labels = {}
        btns_labels = list([None]) + search(CRC.configs[self.configKey].cnf_types_cnf_re['choice'],
                                            cnf_ln).group().split(';')
        var = IntVar()
        _container = Label(container, height=1)

        self._expand_all_wg(_container)

        def _set(_val): self.val, self.cnf, self.see = _val, _val, _val

        for n, btn in enumerate(btns_labels):
            self.btns_labels |= {btns_labels[n]: Radiobutton(
                _container,
                text=str(btns_labels[n]),
                variable=var,
                relief="solid",
                height=1,
                bd=0,
                font=CRC.fonts[self.configKey].main_font,
                value=n,
                command=lambda s=str(btns_labels[n]): _set(s)
            )}
            self.btns_labels[btns_labels[n]].grid(column=n, row=0)
            self._expand_all_wg(self.btns_labels[btns_labels[n]])
        _container.grid(**GridKwargs | grid_kwargs)
        self.btns_labels[None].select()

    def setval(self, value):
        try:
            self.btns_labels[value].select()
        except KeyError as e:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_corresponding_val % e)
            value = None
            self.btns_labels[value].select()
        self.val, self.see, self.cnf = value, value, value

    def get(self):
        return self.cnf

    def setcolor(self):
        self.set_color(tuple(self.btns_labels.values()),
                       tuple([CRC.colors[self.configKey].color_choice_bg for _ in self.btns_labels]),
                       tuple([CRC.colors[self.configKey].color_choice_fg for _ in self.btns_labels]))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state(tuple(self.btns_labels.values()),
                                               tuple(['color_choice_bg' for _ in self.btns_labels]),
                                               tuple(['color_choice_fg' for _ in self.btns_labels]), setmeth)


class type_collect(ButtonEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        self.val = None
        self.see = ""
        self.cnf = None
        self.t = ""
        self.n_select = list()
        self.btns_labels = []
        self.btns = []
        self.type_cnf = compile(
            search(CRC.configs[configKey].cnf_types_cnf_re['collect'], cnf_ln).group()
        )
        id2val = dict()
        _vtypes = {'i': int, 's': str}
        _n = -1
        for _l in search(self.type_cnf, cnf_ln).group().split(';'):
            _p, _l, _t, _v = _l.split(':')
            if _n == -1:
                self.t = "<" + _p + ">"
                _n += 1
                continue
            if (platform == "linux" and _p == "w") or (platform == "win32" and _p == "l"):
                continue
            _v = _vtypes[_t].__call__(_v)
            self.btns_labels.append(_l)
            self.btns.append(None)
            id2val[_n] = _v
            _n += 1
        if self.t == "<idict>":
            self.val2id = {i: i for i in range(len(id2val))}
        elif self.t == "<tuple>":
            self.val2id = {sig: i for i, sig in id2val.items()}

        def select():
            def _set(n_):
                self.entry.delete(0, END)
                if n_ in self.n_select:
                    self.n_select.remove(n_)
                else:
                    self.n_select.append(n_)
                    self.n_select.sort()
                if self.t == "<idict>":
                    self.val = {i: id2val[i] for i in self.n_select}
                    self.cnf = self.val
                elif self.t == "<tuple>":
                    self.val = tuple([id2val[i] for i in self.n_select])
                    self.cnf = self.val
                self.entry.insert(0, str(self.val))

            window = Tk()
            window.title(self.t)
            window.resizable(False, False)
            window.focus_force()
            window.attributes('-topmost', True)
            window.bind("<Escape>", lambda _: window.destroy())
            widget_close.active_windows.add(window)
            for n, ln in enumerate(self.btns_labels):
                self.btns[n] = Checkbutton(
                    window,
                    text=str(ln),
                    font=CRC.fonts[self.configKey].main_font,
                    command=lambda i=n: _set(i)
                )
                if n in self.n_select: self.btns[n].select()
                self.btns[n].pack(anchor=W)
            window.mainloop()

        ButtonEntryBase.__init__(self, container, configKey, txt_cell, " + ", select, **grid_kwargs)

    def setval(self, value):
        if value is None:
            self.val, self.cnf = value, value
            self.see = CRC.strings[self.configKey].label_none
            self.n_select.clear()
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
            self.n_select.clear()
        else:
            self.val, self.cnf = value, value
            self.see = str(value)
            self.n_select = [self.val2id[i] for i in value]
        self.del_insert(self.entry, self.see)

    def get(self):
        return self.cnf

    def setcolor(self):
        self.set_color((self.button, self.entry),
                       (CRC.colors[self.configKey].color_collect_button_bg,
                        CRC.colors[self.configKey].color_collect_entry_bg),
                       (CRC.colors[self.configKey].color_collect_button_fg,
                        CRC.colors[self.configKey].color_collect_entry_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.button, self.entry),
                                               ('color_collect_button_bg', 'color_collect_entry_bg'),
                                               ('color_collect_button_fg', 'color_collect_entry_fg'), setmeth)


class type_bool(BaseMethods):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        BaseMethods.__init__(self, configKey, txt_cell)
        self.val = None
        self.see = ""
        self.cnf = None
        self.btns_bool = [None, False, True]
        radio_kw = {
            'variable': IntVar(),
            'relief': "solid",
            'height': 1,
            'bd': 0,
            'font': CRC.fonts[self.configKey].main_font
        }
        _container = Label(container, height=1)

        def _set(_val): self.val, self.cnf, self.see = _val, _val, _val

        self.btns_bool[0] = Radiobutton(
            _container,
            text="None",
            value=0,
            command=lambda: _set(None),
            **radio_kw
        )
        self.btns_bool[0].grid(column=0, row=0)
        self.btns_bool[1] = Radiobutton(
            _container,
            text="False",
            value=1,
            command=lambda: _set(False),
            **radio_kw
        )
        self.btns_bool[1].grid(column=1, row=0)
        self.btns_bool[2] = Radiobutton(
            _container,
            text="True",
            value=2,
            command=lambda: _set(True),
            **radio_kw
        )
        self.btns_bool[2].grid(column=2, row=0)
        _container.grid(**GridKwargs | grid_kwargs)
        self._expand_all_wg(_container)
        self._expand_all_wg(tuple(self.btns_bool))

    def setval(self, value: bool):
        self.val, self.cnf = value, value
        self.see = value
        self.btns_bool[{None: 0, False: 1, True: 2}[value]].select()

    def get(self):
        return self.cnf

    def setcolor(self):
        self.set_color(tuple(self.btns_bool),
                       tuple([CRC.colors[self.configKey].color_bool_bg for _ in self.btns_bool]),
                       tuple([CRC.colors[self.configKey].color_bool_fg for _ in self.btns_bool]))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state(tuple(self.btns_bool),
                                               tuple(['color_bool_bg' for _ in self.btns_bool]),
                                               tuple(['color_bool_fg' for _ in self.btns_bool]), setmeth)


class type_intpair(LabelEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        self.val = [None, None]
        self.see = ["", ""]
        self.cnf = None
        self.type_cnf = search(CRC.configs[configKey].cnf_types_cnf_re['intpair'], cnf_ln).group().split(";")
        _labels = []
        for i in range(len(self.type_cnf)):
            _l, _r = self.type_cnf[i].split(':')
            _labels.append(_l)
            self.type_cnf[i] = compile(_r)
        LabelEntryBase.__init__(self, container, configKey, txt_cell, *[f"{_l}:" for _l in _labels],
                                ent_width=CRC.geo[configKey].entry_intpair, **grid_kwargs)
        self.varname = varname
        [setattr(e, "varname", self.varname) for e in self.entrys]

    def setval(self, value: list):
        for n, e in enumerate(self.entrys):
            e.config(bg=[CRC.colors[self.configKey].color_intpair_entry1_bg,
                         CRC.colors[self.configKey].color_intpair_entry2_bg][n])
        if value is None:
            self.val, self.cnf = [None, None], None
            self.see = [CRC.strings[self.configKey].label_none, CRC.strings[self.configKey].label_none]
        elif str(value).lower() == "false":
            self.val, self.cnf = [False, False], False
            self.see = [CRC.strings[self.configKey].label_disabled, CRC.strings[self.configKey].label_disabled]
        elif isinstance(value, list) or isinstance(value, tuple):
            value = list(value)
            part = False
            valid_cnf = True
            _false = False
            for n in range(len(self.entrys)):
                if isinstance(value[n], int):
                    part = part ^ True
                    self.val[n], self.see[n] = value[n], value[n]
                elif str(value[n]).lower() == "false" or value[n] == CRC.strings[self.configKey].label_disabled:
                    _false, self.val[n], self.see[n] = True, False, CRC.strings[self.configKey].label_disabled
                elif isinstance(value[n], str) and search(self.type_cnf[n], value[n]):
                    part = part ^ True
                    self.val[n], self.see[n] = int(value[n]), value[n]
                elif isinstance(value[n], str):
                    if not value[n]:
                        self.val[n], self.see[n] = None, ""
                    elif value[n] == CRC.strings[self.configKey].label_none:
                        self.val[n], self.see[n] = None, CRC.strings[self.configKey].label_none
                    elif value[n] == CRC.strings[self.configKey].label_ireq:
                        self.val[n], self.see[n] = None, CRC.strings[self.configKey].label_ireq
                    else:
                        self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_int)
                        self.val[n], self.see[n] = None, value[n]
                        self.entrys[n].config(bg=CRC.colors[self.configKey].color_error_bg)
                    value[n] = None
                    self.cnf = None
                    valid_cnf = False
            if part: [self.see.__setitem__(n, CRC.strings[self.configKey].label_ireq) for n in range(len(self.type_cnf))
                      if self.val[n] is None]
            if valid_cnf: self.cnf = self.val
            if _false: self.cnf = False
        for n in range(len(self.entrys)):
            self.del_insert(self.entrys[n], self.see[n])

    def get(self):
        self.setval([self.entrys[n].get().strip() for n in range(len(self.type_cnf))])
        return self.cnf if self.cnf else None

    def fill(self, val):
        if not isinstance(val, list) and not isinstance(val, tuple): return
        _val = [None, None]
        for n in range(len(self.type_cnf)):
            if isinstance(self.val[n], int):
                _val[n] = self.val[n]
            else:
                _val[n] = val[n]
        self.setval(_val)

    def setcolor(self):
        self.set_color(tuple(self.labels + self.entrys),
                       (CRC.colors[self.configKey].color_intpair_label1_bg,
                        CRC.colors[self.configKey].color_intpair_label2_bg,
                        CRC.colors[self.configKey].color_intpair_entry1_bg,
                        CRC.colors[self.configKey].color_intpair_entry2_bg),
                       (CRC.colors[self.configKey].color_intpair_label1_fg,
                        CRC.colors[self.configKey].color_intpair_label2_fg,
                        CRC.colors[self.configKey].color_intpair_entry1_fg,
                        CRC.colors[self.configKey].color_intpair_entry2_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state(tuple(self.labels + self.entrys),
                                               ('color_intpair_label1_bg', 'color_intpair_label2_bg',
                                                'color_intpair_entry1_bg', 'color_intpair_entry2_bg'),
                                               ('color_intpair_label1_fg', 'color_intpair_label2_fg',
                                                'color_intpair_entry1_fg', 'color_intpair_entry2_fg'), setmeth)


class type_wfile(ButtonEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        ButtonEntryBase.__init__(self, container, configKey, txt_cell, " + ", lambda: self.setval(asksaveasfilename()),
                                 "nul", lambda: self.setval(None), **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = int(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['wfile'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_wfile_entry_bg)
        if value == () or value is None:
            self.val, self.cnf = None, devnull
            self.see = devnull
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif isinstance(value, str) and value.strip() == "":
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_disabled
        elif value == devnull or access(search(CRC.PATH_RE, (value := path.realpath(value))).group(), self.type_cnf):
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_notfound)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.button2, self.button, self.entry),
                       (CRC.colors[self.configKey].color_wfile_nul_bg, CRC.colors[self.configKey].color_wfile_button_bg,
                        CRC.colors[self.configKey].color_wfile_entry_bg),
                       (CRC.colors[self.configKey].color_wfile_nul_fg, CRC.colors[self.configKey].color_wfile_button_fg,
                        CRC.colors[self.configKey].color_wfile_entry_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.button2, self.button, self.entry),
                                               ('color_wfile_nul_bg', 'color_wfile_button_bg', 'color_wfile_entry_bg'),
                                               ('color_wfile_nul_fg', 'color_wfile_button_fg', 'color_wfile_entry_fg'),
                                               setmeth)


class type_rfile(ButtonEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        ButtonEntryBase.__init__(self, container, configKey, txt_cell, " + ", lambda: self.setval(askopenfilename()),
                                 **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = int(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['rfile'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_rfile_entry_bg)
        if value == () or value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif isinstance(value, str) and value.strip() == "":
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_disabled
        elif access(value := path.realpath(value), self.type_cnf) and path.isfile(value):
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_notfound)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.button, self.entry),
                       (CRC.colors[self.configKey].color_rfile_button_bg,
                        CRC.colors[self.configKey].color_rfile_entry_bg),
                       (CRC.colors[self.configKey].color_rfile_button_fg,
                        CRC.colors[self.configKey].color_rfile_entry_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.button, self.entry),
                                               ('color_rfile_button_bg', 'color_rfile_entry_bg'),
                                               ('color_rfile_button_fg', 'color_rfile_entry_fg'), setmeth)


class type_re(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell=None, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_re, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = compile(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['re'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_re_entry_bg)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif search(self.type_cnf, value):
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_re)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_re_entry_bg,),
                       (CRC.colors[self.configKey].color_re_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_re_entry_bg',),
                                               ('color_re_entry_fg',), setmeth)


class type_fsc(LabelEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        LabelEntryBase.__init__(self, container, configKey, txt_cell, "IV:", "Part:", "Prio:", "Hops:",
                                ent_width=CRC.fonts[configKey]._main_size, **grid_kwargs)
        self.val = [None, None, None, None]
        self.see = ["", "", "", ""]
        self.cnf = None
        self.varname = varname
        [setattr(e, "varname", self.varname) for e in self.entrys]

    def setval(self, value: list[int, int, int, int]):
        [e.config(bg=CRC.colors[self.configKey].color_fsc_all_bg) for e in self.entrys]
        if value is None:
            self.val, self.cnf = [None, None, None, None], None
            self.see = [CRC.strings[self.configKey].label_none for _ in range(4)]
        elif str(value).lower() == "false":
            self.val, self.cnf = [False, False, False, False], False
            self.see = [CRC.strings[self.configKey].label_disabled for _ in range(4)]
        elif isinstance(value, list) or isinstance(value, tuple):
            value = list(value)
            if isinstance(value[1], tuple):
                value = [value[0], value[1][0], value[1][1], value[2]]
            part = 0
            _false = False
            for n in range(len(value)):
                if str(value[n]).lower() == "false" or value[n] == CRC.strings[self.configKey].label_disabled:
                    _false, self.val[n], self.see[n] = True, False, CRC.strings[self.configKey].label_disabled
                    part += 1
                if isinstance(value[n], int):
                    part += 1
                    self.val[n], self.see[n] = value[n], value[n]
                elif isinstance(value[n], str) and search("^[0-9]+$", value[n]):
                    _ranges = ((0, 1000), (0, 2), (1, 10), (1, 10))
                    self.val[n], self.see[n] = int(value[n]), value[n]
                    if self.val[n] not in range(*_ranges[n]):
                        self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_fsc % _ranges[n])
                        self.val[n], self.see[n] = None, value[n]
                        self.entrys[n].config(bg=CRC.colors[self.configKey].color_error_bg)
                        continue
                    part += 1
                elif isinstance(value[n], str):
                    if not value[n]:
                        self.val[n], self.see[n] = None, ""
                    elif value[n] == CRC.strings[self.configKey].label_none:
                        self.val[n], self.see[n] = None, CRC.strings[self.configKey].label_none
                    if value[n] == CRC.strings[self.configKey].label_ireq:
                        self.val[n], self.see[n] = None, CRC.strings[self.configKey].label_ireq
                    value[n] = None
                    self.cnf = None
                else:
                    self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_int)
                    self.val[n], self.see[n] = None, value[n]
                    self.entrys[n].config(bg=CRC.colors[self.configKey].color_error_bg)
            if part and part != 4:
                [self.see.__setitem__(n, CRC.strings[self.configKey].label_ireq) for n in range(4) if
                 self.val[n] is None]
            if part == 4: self.cnf = (self.val[0], (self.val[1], self.val[2]), self.val[3])
            if _false: self.cnf = False
        for n in range(4):
            self.del_insert(self.entrys[n], self.see[n])

    def fill(self, val):
        if not (isinstance(val, list) or isinstance(val, tuple)): return
        _val = [None, None, None, None]
        if isinstance(self.val[0], int):
            _val[0] = self.val[0]
        else:
            _val[0] = val[0]
        if isinstance(self.val[1], int):
            _val[1] = self.val[1]
        else:
            _val[1] = val[1][0]
        if isinstance(self.val[2], int):
            _val[2] = self.val[2]
        else:
            _val[2] = val[1][1]
        if isinstance(self.val[3], int):
            _val[3] = self.val[3]
        else:
            _val[3] = val[2]
        self.setval(_val)

    def get(self):
        self.setval([e.get().strip() for e in self.entrys])
        return self.cnf

    def setcolor(self):
        self.set_color(tuple(self.labels + self.entrys),
                       tuple([CRC.colors[self.configKey].color_fsc_all_bg for _ in self.labels + self.entrys]),
                       tuple([CRC.colors[self.configKey].color_fsc_all_fg for _ in self.labels + self.entrys]))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state(tuple(self.labels + self.entrys),
                                               tuple(['color_fsc_all_bg' for _ in self.labels + self.entrys]),
                                               tuple(['color_fsc_all_fg' for _ in self.labels + self.entrys]), setmeth)


class type_pars(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_pars, **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = compile(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['pars'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_pars_entry_bg)
        if value is None:
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif isinstance(value, str) and value.strip() == "":
            self.val, self.cnf = "", ""
            self.see = CRC.strings[self.configKey].label_str
        elif search(self.type_cnf, value):
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_pars)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_pars_entry_bg,),
                       (CRC.colors[self.configKey].color_pars_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_pars_entry_bg',),
                                               ('color_pars_entry_fg',), setmeth)


class type_rformfile(ButtonEntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        ButtonEntryBase.__init__(self, container, configKey, txt_cell, " + ", lambda: self.setval(asksaveasfilename()),
                                 **grid_kwargs)
        self.val = None
        self.see = ""
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = int(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['rformfile'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.entry.config(bg=CRC.colors[self.configKey].color_rformfile_entry_bg)
        if value == () or value is None or (isinstance(value, str) and value.strip() == ""):
            self.val, self.cnf = None, None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif access(search(CRC.PATH_RE, (value := path.realpath(value))).group(), self.type_cnf) and not path.isdir(value):
            if not search("[^/\\\%]*%s[^/\\\%]*$", value):
                self.val, self.cnf = None, None
                self.see = value
                self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
                return self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_format)
            self.val, self.cnf = value, value
            self.see = value
        else:
            self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_notfound)
            self.val, self.cnf = None, None
            self.see = value
            self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
        self.del_insert(self.entry, self.see)

    def setcolor(self):
        self.set_color((self.button, self.entry),
                       (CRC.colors[self.configKey].color_rformfile_button_bg,
                        CRC.colors[self.configKey].color_rformfile_entry_bg),
                       (CRC.colors[self.configKey].color_rformfile_button_fg,
                        CRC.colors[self.configKey].color_rformfile_entry_fg))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.button, self.entry),
                                               ('color_rformfile_button_bg', 'color_rformfile_entry_bg'),
                                               ('color_rformfile_button_fg', 'color_rformfile_entry_fg'), setmeth)


class type_list(EntryBase):

    def __init__(self, container, varname, cnf_ln, configKey, txt_cell, **grid_kwargs):
        EntryBase.__init__(self, container, configKey, txt_cell, CRC.geo[configKey].entry_list, **grid_kwargs)
        self.val = None
        self.see = str()
        self.cnf = None
        self.varname = varname
        self.entry.varname = self.varname
        self.type_cnf = compile(
            search(CRC.configs[self.configKey].cnf_types_cnf_re['list'], cnf_ln).group()
        )

    def setval(self, value):
        if value == self.see: return
        self.see = str()
        self.entry.config(bg=CRC.colors[self.configKey].color_list_entry_bg)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.val, self.cnf = set(), None
            self.see = CRC.strings[self.configKey].label_none
        elif str(value).lower() == "false":
            self.val, self.cnf = False, False
            self.see = CRC.strings[self.configKey].label_disabled
        elif isinstance(value, list):
            self.val, self.cnf = set(value), set(value)
            self.see = str().join([ip + ";" for ip in value])
        else:
            self.val = set()
            for ip in value.split(';'):
                if not (ip := ip.strip()): continue
                if not search(self.type_cnf, ip):
                    self.txt_cell.insert(self.varname, CRC.strings[self.configKey].errmsg_list)
                    self.entry.config(bg=CRC.colors[self.configKey].color_error_bg)
                    continue
                self.val.add(ip)
                self.see += ip + ';'
            self.cnf = self.val
        if not self.val: self.val = None
        self.del_insert(self.entry, self.see)

    def get(self):
        self.setval(self.entry.get().strip())
        return list(self.cnf) if self.cnf else None

    def setcolor(self):
        self.set_color((self.entry,),
                       (CRC.colors[self.configKey].color_list_entry_bg,),
                       (CRC.colors[self.configKey].color_list_entry_fg,))

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state((self.entry,),
                                               ('color_list_entry_bg',),
                                               ('color_list_entry_fg',), setmeth)
