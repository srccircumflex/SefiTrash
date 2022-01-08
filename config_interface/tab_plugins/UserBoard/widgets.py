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

from tkinter import Label, Checkbutton, IntVar, Button, Tk, Radiobutton
from tkinter import LEFT, W, X, E, NSEW, EW
from tkinter.messagebox import askyesnocancel, showerror
from _tkinter import TclError

from re import search

from _rc import configurations
from sec.fTools import DefIfEndIf
from sec.vTools import mk_login

from config_interface import ROOT_TK
from config_interface._rc import _run as CRC
from config_interface.prc import configtypeobjs as COJ
from config_interface.wdg.InfoPopUp import InfoPopUp
from config_interface.wdg.plugin_widgets import ScrollCell, TextCell
from config_interface.tab_plugins.UserBoard import configKey, TARGET_ATTR, TARGET_UNIT, msg_strings

ROOT_TK.option_add('*Dialog.msg.font', 'Consolas 8')
ROOT_TK.option_add('*Dialog.msg.width', 64)


class UserLine:

    def __init__(self, master_cell: ScrollCell, _id, txt_cell):

        self.id = _id

        self.label = Label(master_cell,
                           relief=CRC.configs[configKey].cnfrow_relief,
                           height=CRC.configs[configKey].cnfrow_height
                           )

        self.username = COJ.type_str(self.label, str(self.id), "", configKey, txt_cell, column=0)

        _l1 = Label(self.label, text=" |  ", font=CRC.fonts.main_font)
        _l1.grid(row=0, column=1)

        self.livetime = COJ.type_intpair(self.label, str(self.id), "0$intpair;{half life:^[0-9]+$}$", configKey,
                                         txt_cell, column=2)

        _l2 = Label(self.label, text=" |  ", font=CRC.fonts.main_font)
        _l2.grid(row=0, column=3)

        self.lapslim = COJ.type_intpair(self.label, str(self.id), "0$intpair;{laps lim:^[0-9]+$}$", configKey, txt_cell,
                                        column=4)

        _l3 = Label(self.label, text=" |  ", font=CRC.fonts.main_font)
        _l3.grid(row=0, column=5)

        self.labsdel_v = IntVar()
        self.labsdel = Checkbutton(self.label, text="laps del", variable=self.labsdel_v,
                                   font=CRC.fonts.main_font,
                                   compound=LEFT)
        self.labsdel.grid(row=0, column=6)

        _l4 = Label(self.label, text=" |  ", font=CRC.fonts.main_font)
        _l4.grid(row=0, column=7)

        self.fsc = COJ.type_fsc(self.label, str(self.id), "", configKey, txt_cell, column=8)

        _l5 = Label(self.label, text=" |  ", font=CRC.fonts.main_font)
        _l5.grid(row=0, column=9)

        self.delflag_v = IntVar()
        self.delflag = Checkbutton(self.label, text="del flag", variable=self.delflag_v,
                                   font=CRC.fonts.main_font,
                                   compound=LEFT)
        self.delflag.grid(row=0, column=10)

        _l6 = Label(self.label, text=" |  row-id: %-100d" % self.id, font=CRC.fonts.main_font)
        _l6.grid(row=0, column=11)

        self.label.pack(anchor=W, fill=X)

        for w in (self.label, _l1, _l2, _l3, _l4, _l5, _l6, self.labsdel, self.delflag):
            master_cell.scroll_update(w)

        for w in (self.username, self.livetime, self.lapslim, self.fsc):
            for _w in w.all_wg:
                master_cell.scroll_update(_w, "V")

    def source_ln(self, source_ln):
        if username := search(b"^\w+", source_ln):
            self.username.setval(username.group())
        if livetime := search(b"(?<=lft:)[0-9]+", source_ln):
            self.livetime.setval([int(livetime.group())])
        if lapslim := search(b"(?<=lpl:)[0-9]+", source_ln):
            self.lapslim.setval([int(lapslim.group())])
        if search(b"lpd:1", source_ln):
            self.labsdel.select()
        if fsc := search(b"(?<=bpp:)\d+[-+]\d+\.\d+", source_ln):
            fsc = fsc.group()
            val = [None, None, None, None]
            val[0] = int(search(b"\d+", fsc).group())
            val[1] = (1 if b"+" in fsc else 0)
            val[2] = int(search(b"(?<=[+-])\d+(?=\.)", fsc).group())
            val[3] = int(search(b"(?<=\.)\d+", fsc).group())
            self.fsc.setval(val)
        if search(b"<del>", source_ln):
            self.delflag.select()

    def get_fsc(self, independent=False):
        fsc = self.fsc.get()
        bpp = ""
        if fsc:
            bpp = f"bpp:{fsc[0]}{'+' if fsc[1][0] else '-'}{fsc[1][1]}.{fsc[2]}"
            if independent:
                if not (username := self.username.get()):
                    return
                return ("%-32s%s" % (username, bpp)).strip() + '\n'
        return bpp

    def get_ln(self, include_fsc=False):
        username = self.username.get()
        if not username:
            return
        livetime = self.livetime.get()
        livetime = ("lft:%d" % livetime[0] if livetime else "")
        lapslim = self.lapslim.get()
        lapslim = ("lpl:%d" % lapslim[0] if lapslim else "")
        bpp = (self.get_fsc() if include_fsc else "")
        delflag = ("<del>" if self.delflag_v.get() else "")

        return """%-18s %-18s %-8s lpd:%-8d %-18s %s
        """ % (username, livetime, lapslim, self.labsdel_v.get(), bpp, delflag)

    def forget(self):
        self.label.destroy()


class _Cells:
    def __init__(self, _self):
        self.err_text = TextCell(
            _self.tabFrame,
            configKey,
            sticky=NSEW,
            row=2,
            rowspan=2,
            column=1
        )

        self.master_cell = ScrollCell(
            _self.tabFrame,
            configKey,
            cell_kwargs={'height': CRC.geo.main_height // 2,
                         'width': CRC.geo.main_width * 2},
            scrollbar_kwargs={'width': CRC.geo.scrollbar_width}
        )

        self.master_cell.grid(sticky=EW,
                              row=1,
                              column=0,
                              columnspan=2)

        self.log_text = TextCell(
            _self.tabFrame,
            configKey,
            sticky=NSEW,
            row=3,
            column=0
        )

        ___ico_height = 12

        self.err_text.text.config(
            height=(CRC.geo.main_height // 2 - ___ico_height) // CRC.fonts.height_divisor
        )
        self.err_text.insert(_str=msg_strings.QUICK_GUIDE)
        self.log_text.insert(_str=msg_strings.DESCRIPTION)


class _Data(_Cells):

    def __init__(self, _self):
        _Cells.__init__(self, _self)

        self._self = _self

        self.user_lines = dict()

        self.file_entry = COJ.type_rfile(
            _self.tabFrame,
            "",
            " 0$rfile;{6}$",
            configKey,
            self.err_text,
            sticky=W,
            row=0,
            column=0
        )

        self.source_button = Button(
            **self.file_entry.button_kw,
            text=" >>> ",
            image=CRC.fonts[configKey].ico_source,
            command=self.source
        )
        self.source_button.grid(sticky=E, row=0, column=4)
        InfoPopUp(self.source_button,
                  ["Source File"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )

        self.file_out = COJ.type_wfile(
            _self.tabFrame,
            "",
            " 0$wfile;{6}$",
            configKey,
            self.err_text,
            sticky=W,
            row=2,
            column=0
        )

        self.write_button = Button(
            **self.file_out.button_kw,
            text=" out ",
            image=CRC.fonts[configKey].ico_save,
            command=self.write_out
        )
        self.write_button.grid(sticky=W, row=0, column=0)
        InfoPopUp(self.write_button,
                  ["Write out"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )

        self.incl_fsc_v = IntVar()
        self.incl_fsc = Checkbutton(
            **self.file_out.button_kw,
            text=" include FSC-peppers ",
            variable=self.incl_fsc_v
        )
        self.incl_fsc.grid(sticky=W, row=0, column=1)
        self.incl_fsc.select()
        InfoPopUp(self.incl_fsc,
                  ["IV", "Part", "Prio", "Hops"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )

        self.fsc_out = COJ.type_wfile(
            self.file_out.button_kw['master'],
            "",
            " 0$wfile;{6}$",
            configKey + "2",
            self.err_text,
            sticky=W,
            row=0,
            column=4
        )

        self.write_fsc_button = Button(
            **self.fsc_out.button_kw,
            text=" fsc ",
            image=CRC.fonts[configKey].ico_fsc_out,
            command=self.write_fsc_out
        )
        self.write_fsc_button.grid(sticky=W, row=0, column=1)
        InfoPopUp(self.write_fsc_button,
                  ["Write FSC-Peppers in separate independent file"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )

        self.add_ln()

        self.windows = set()

    def source(self):

        for u_ln in self.user_lines.values():
            u_ln.forget()

        self.user_lines = dict()

        if not (path := self.file_entry.get()):
            self.add_ln()
            return

        self._self.Groot.MAIN_TAB.cnf_units[TARGET_UNIT][TARGET_ATTR].cnf.setval(path)
        self.fsc_out.setval(path)
        self.file_out.setval(path)

        defif = DefIfEndIf(path, *configurations.IFDEFENDIF[TARGET_ATTR])
        if defif.configured:
            _id = 0
            read_rc = defif.read_rc()
            while True:
                try:
                    ln = next(read_rc)
                    self.user_lines.setdefault(
                        _id,
                        UserLine(self.master_cell, _id, self.err_text)
                    )
                    self.user_lines[_id].source_ln(ln)
                    self.user_lines[_id].username.entry.bind("<Control-Button-1>",
                                                             lambda _, row=self.user_lines[_id]: self.create_login(row))
                    _id += 1
                except StopIteration:
                    self.add_ln()
                    break

    def write_out(self):
        _file = self.file_out.get()
        _incl = self.incl_fsc_v.get()
        try:
            defif = DefIfEndIf(_file, *configurations.IFDEFENDIF[TARGET_ATTR])
        except Exception as e:
            return self.err_text.insert(_str=msg_strings.EXCEPTION % e)
        if defif.configured:
            self.log_text.insert(_str=msg_strings.SEPARATOR128)
            insert_rc = defif.insert_rc()
            next(insert_rc)
            for u_ln in self.user_lines.values():
                if _ln := u_ln.get_ln(_incl):
                    self.log_text.insert(_str=msg_strings.INSERT % _ln.strip())
                    insert_rc.send(_ln.encode())
            try:
                insert_rc.send(None)
            except StopIteration:
                pass
            self.log_text.insert(_str=msg_strings.INSERTED_INTO % (_file, bool(_incl)))
        else:
            self.log_text.insert(_str=msg_strings.SEPARATOR128)
            try:
                with open(_file, "w") as f:
                    f.write(configurations.IFDEFENDIF[TARGET_ATTR][0].decode() + '\n')
                    for u_ln in self.user_lines.values():
                        if _ln := u_ln.get_ln(_incl):
                            self.log_text.insert(_str=msg_strings.WRITE % _ln.strip())
                            f.write(_ln)
                    f.write(configurations.IFDEFENDIF[TARGET_ATTR][1].decode() + '\n')
            except Exception as e:
                return self.err_text.insert(_str=msg_strings.EXCEPTION % e)
            self.log_text.insert(_str=msg_strings.CREATED % (_file, bool(_incl)))

    def write_fsc_out(self):
        _file = self.fsc_out.get()
        try:
            defif = DefIfEndIf(_file, *configurations.IFDEFENDIF[TARGET_ATTR])
        except Exception as e:
            return self.err_text.insert(_str=msg_strings.EXCEPTION % e)
        if defif.configured:
            self.log_text.insert(_str=msg_strings.SEPARATOR128)
            insert_rc = defif.insert_rc()
            next(insert_rc)
            for u_ln in self.user_lines.values():
                if _ln := u_ln.get_fsc(True):
                    self.log_text.insert(_str=msg_strings.INSERT % _ln.strip())
                    insert_rc.send(_ln.encode())
            try:
                insert_rc.send(None)
            except StopIteration:
                pass
            self.log_text.insert(_str=msg_strings.INSERTED_INTO_P % _file)
        else:
            self.log_text.insert(_str=msg_strings.SEPARATOR128)
            try:
                with open(_file, "w") as f:
                    f.write(configurations.IFDEFENDIF[TARGET_ATTR][0].decode() + '\n')
                    for u_ln in self.user_lines.values():
                        if _ln := u_ln.get_fsc(True):
                            self.log_text.insert(_str=msg_strings.WRITE % _ln.strip())
                            f.write(_ln)
                    f.write(configurations.IFDEFENDIF[TARGET_ATTR][1].decode() + '\n')
            except Exception as e:
                return self.err_text.insert(_str=msg_strings.EXCEPTION % e)
            self.log_text.insert(_str=msg_strings.CREATED_P % _file)

    def add_ln(self, event=None):
        ids = list(self.user_lines)
        _id = (0 if not ids else ids[-1])
        if event and not self.user_lines[_id].get_ln():
            return
        elif _id in self.user_lines:
            self.user_lines[_id].username.entry.unbind("<Tab>")
            self.user_lines[_id].livetime.entrys[0].unbind("<Tab>")
            self.user_lines[_id].lapslim.entrys[0].unbind("<Tab>")
            self.user_lines[_id].username.entry.bind("<Tab>", lambda _, row=self.user_lines[_id]: row.username.get())
            self.user_lines[_id].livetime.entrys[0].bind("<Tab>",
                                                         lambda _, row=self.user_lines[_id]: row.livetime.get())
            self.user_lines[_id].lapslim.entrys[0].bind("<Tab>", lambda _, row=self.user_lines[_id]: row.lapslim.get())
        _id += 1
        self.user_lines.setdefault(
            _id,
            UserLine(self.master_cell, _id, self.err_text)
        )
        self.user_lines[_id].username.entry.bind("<Control-Button-1>",
                                                 lambda _, row=self.user_lines[_id]: self.create_login(row))
        self.user_lines[_id].username.entry.bind("<Tab>", self.add_ln)
        self.user_lines[_id].livetime.entrys[0].bind("<Tab>", self.add_ln)
        self.user_lines[_id].lapslim.entrys[0].bind("<Tab>", self.add_ln)

    def create_login(self, user_row: UserLine, _loop=False) -> [str, None]:
        board_username = user_row.username.get()
        board_peppers = user_row.fsc.get()
        BASIC_FSC_PEPPER = self._self.Groot.MAIN_TAB.cnf_units["Verification"]["BASIC_FSC_PEPPER"].cnf.get()
        FSC_HOST_SPICE_FILE = self._self.Groot.MAIN_TAB.cnf_units["Verification"]["FSC_HOST_SPICE_FILE"].cnf.get()
        FSC_HOST_XF = self._self.Groot.MAIN_TAB.cnf_units["Verification"]["FSC_HOST_XF"].cnf.get()
        FSC_HOST_TABLE_FILE = self._self.Groot.MAIN_TAB.cnf_units["Verification"]["FSC_HOST_TABLE_FILE"].cnf.get()
        FSC_PEPPER_HOST = self._self.Groot.MAIN_TAB.cnf_units["Verification"]["FSC_PEPPER_HOST"].cnf.get()
        LOC_ENC = self._self.Groot.MAIN_TAB.cnf_units["Development"]["LOC_ENC"].cnf.get()

        if False in (
                bool(FSC_HOST_SPICE_FILE), bool(FSC_HOST_XF), bool(FSC_HOST_TABLE_FILE), bool(FSC_PEPPER_HOST),
                bool(LOC_ENC)
        ) or not (BASIC_FSC_PEPPER or board_peppers) or not board_username:
            if user_row.id + 1 < len(self.user_lines):
                return
            _err_message = msg_strings.ERR_CONF_REQ % (
                user_row.id,
                f"{FSC_HOST_SPICE_FILE=}",
                f"{FSC_HOST_XF=}",
                f"{FSC_HOST_TABLE_FILE=}",
                f"{FSC_PEPPER_HOST=}",
                f"{LOC_ENC=}",
                f'{BASIC_FSC_PEPPER=}',
                f'{board_peppers=}',
                f'{board_username=}'
            )

            self.err_text.insert(
                _str=msg_strings.WRAP84 % _err_message
            )

            if _loop and (BASIC_FSC_PEPPER or board_peppers):
                if askyesnocancel(msg_strings.ERR_TITLE % user_row.id,
                                  msg_strings.WRAP32ASK % _err_message,
                                  icon='warning'):
                    raise EOFError
            else:
                showerror(msg_strings.ERR_TITLE % user_row.id, msg_strings.WRAP32 % _err_message)

            return

        AUTH_CONF = {
            'spc': FSC_HOST_SPICE_FILE % board_username,
            'lin': FSC_HOST_XF % board_username,
            'hst': FSC_HOST_TABLE_FILE % board_username,
            'ppp': FSC_PEPPER_HOST % board_username,
            'bpp': (board_peppers if board_peppers else BASIC_FSC_PEPPER)
        }

        window = Tk()
        window.resizable(False, False)
        window.title(board_username)
        window.focus_force()
        window.attributes('-topmost', True)
        window.config(bg="#2E3436")
        self.windows.add(window)

        def destroy(*_):
            for w in self.windows.copy():
                try:
                    w.destroy()
                except TclError:
                    pass
                finally:
                    self.windows.remove(w)
            ROOT_TK.bind("<Button>", lambda _: None)

        ROOT_TK.bind("<Control-Button>", lambda _: None)
        window.bind("<Escape>", destroy)
        ROOT_TK.bind("<Button>", destroy)

        _kw1 = {
            'master': window,
            'font': ("Consolas", 8),
            'bg': "#2E3436",
            'fg': "#D3D7CF",
            'compound': "left"
        }
        _kw2 = {
            'master': window,
            'font': ("Consolas", 6),
            'bg': "#2E3436",
            'fg': "#D3D7CF",
            'compound': "left"
        }
        _gkw1 = {'sticky': "w", "padx": 8, "pady": 2}
        _gkw2 = {'sticky': "w", "padx": 8}

        Label(text=msg_strings.label_passph, **_kw1 | {'font': ("Consolas", 10)}).grid(**_gkw1)
        Label(text=msg_strings.label_filecf, **_kw1).grid(row=2, **_gkw1)
        for _l in msg_strings.label_fileln(AUTH_CONF):
            Label(text=_l, **_kw2).grid(_gkw2)
        Label(text=msg_strings.label_encodi, **_kw1).grid(_gkw1)
        Label(text=msg_strings.label_encovl % f"{LOC_ENC}", **_kw2).grid(_gkw2)
        Label(text=msg_strings.label_pepper, **_kw1).grid(_gkw1)

        if BASIC_FSC_PEPPER and board_peppers:
            _v = IntVar()
            _r1 = Radiobutton(variable=_v, value=0, selectcolor="black",
                              command=lambda: AUTH_CONF.__setitem__('bpp', board_peppers),
                              text=msg_strings.label_peppvl % f"{board_peppers=}",
                              **_kw2)
            _r1.grid(_gkw1)
            Radiobutton(variable=_v, value=1, selectcolor="black",
                        command=lambda: AUTH_CONF.__setitem__('bpp', BASIC_FSC_PEPPER),
                        text=msg_strings.label_peppvl % f"{BASIC_FSC_PEPPER=}",
                        **_kw1).grid(_gkw2)
            _r1.select()
        else:
            Label(text=msg_strings.label_peppvl % f"{AUTH_CONF['bpp']}", **_kw1).grid(_gkw2)

        passentry = COJ.type_pass(window, "", " 0$pass;{sha256}$", configKey, None,
                                  column=0, row=1, sticky='ew', pady=6, padx=8)
        passentry.entry.insert(0, msg_strings.PASS_ENTRY)

        def run(*_):
            if not (pw := passentry.get()):
                return showerror(msg_strings.ERR_TITLE % user_row.id, msg_strings.ERR_PASS)
            window.unbind("<Return>")
            window.after(500, window.destroy)

            configurations.AUTH_CONF = {board_username: AUTH_CONF}
            configurations.LOC_ENC = LOC_ENC
            mk_login(board_username, pw)

            if not _loop:
                self.log_text.insert(_str=msg_strings.SEPARATOR128)
                self.log_text.insert(_str=msg_strings.LOGIN_CREATED % (AUTH_CONF['bpp'], board_username, board_username))
                self.log_text.insert(_str=msg_strings.PAIRING_INSTR)
                self.log_text.insert(_str=msg_strings.SEPARATOR128)

            else:
                self.log_text.insert(_str=msg_strings.LOGIN_CREATED % (AUTH_CONF['bpp'], board_username, board_username))

        window.bind("<Return>", run)


class UserLineMethods(_Data):
    def __init__(self, _self):
        _Data.__init__(self, _self)

        self._self = _self

        _container = Label(_self.tabFrame, width=1)
        Label(_container, text="|  ", font=CRC.fonts.main_font).grid(sticky=E, row=0, column=1)
        self.create_logins_button = Button(
            **self.file_entry.button_kw | {'master': _container},
            text=" create logins ",
            image=CRC.fonts[configKey].ico_keys,
            command=self.create_logins
        )
        self.create_logins_button.grid(sticky=E, row=0, column=2)
        InfoPopUp(self.create_logins_button,
                  ["create logins"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )
        Label(_container, text="  ||  ", font=CRC.fonts.main_font).grid(sticky=E, row=0, column=3)
        self.newln_button = Button(
            **self.file_entry.button_kw | {'master': _container},
            text=" new line ",
            image=CRC.fonts[configKey].ico_addrow,
            command=self.add_ln
        )
        self.newln_button.grid(sticky=E, row=0, column=7)
        InfoPopUp(self.newln_button,
                  ["add row"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )
        Label(_container, text="  |  ", font=CRC.fonts.main_font).grid(sticky=E, row=0, column=8)
        self.consume_button = Button(
            **self.file_entry.button_kw | {'master': _container},
            text=" consume ",
            image=CRC.fonts[configKey].ico_consume,
            command=self.consume
        )
        self.consume_button.grid(sticky=E, row=0, column=9)
        InfoPopUp(self.consume_button,
                  ["get all row values"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )
        Label(_container, text="  |  ", font=CRC.fonts.main_font).grid(sticky=E, row=0, column=10)
        self.purge_button = Button(
            **self.file_entry.button_kw | {'master': _container},
            text=" purge ",
            image=CRC.fonts[configKey].ico_purge,
            command=self.purge
        )
        self.purge_button.grid(sticky=E, row=0, column=11)
        InfoPopUp(self.purge_button,
                  ["purge all marked rows"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )
        Label(_container, text="  |", font=CRC.fonts.main_font).grid(sticky=E, row=0, column=12)
        _container.grid(sticky=E, row=0, column=1)

    def consume(self):
        self.log_text.insert(_str=msg_strings.SEPARATOR128)
        for u_ln in self.user_lines.values():
            _ln = u_ln.get_ln(True)
            if _ln:
                self.log_text.insert(_str=msg_strings.GET_LINE % _ln.strip())
        self.log_text.insert(_str=msg_strings.GETTING_LINES)

    def purge(self):
        to_purge = dict()
        for _id, cnf_o in self.user_lines.items():
            if cnf_o.get_ln() and cnf_o.delflag_v.get():
                to_purge.setdefault(_id, cnf_o)
        for _id, cnf_o in to_purge.items():
            cnf_o.forget()
            self.user_lines.pop(_id)

    def create_logins(self):
        self.log_text.insert(_str=msg_strings.SEPARATOR128)
        for user_row in self.user_lines.values():
            try:
                self.create_login(user_row, True)
            except EOFError:
                return self.log_text.insert(_str=msg_strings.BREAK)

        self.log_text.insert(_str=msg_strings.PAIRING_INSTR)
        self.log_text.insert(_str=msg_strings.SEPARATOR128)
