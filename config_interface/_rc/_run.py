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

from tkinter.font import Font, nametofont
from tkinter.colorchooser import askcolor
from tkinter import Scale, Tk, HORIZONTAL, Entry, Checkbutton, Button, PhotoImage

from re import escape, compile, Pattern, search, sub
from sys import platform

from config_interface import configuration_sheet, ROOT_DIR, files_config_file
from config_interface._rc.base_cls import AddRCMain, AddRCChild
from config_interface.sec.auto_close import widget_close


if platform == "win32":
    PATH_RE = compile(".*\\\\")
    SHIFT_TAB = "<Shift-Tab>"
elif platform == "linux":
    PATH_RE = compile(".*/")
    SHIFT_TAB = "<ISO_Left_Tab>"

gui_info_file: str
attr_info_rev_file: str
attr_info_pop_file: str
widget_color_table: str
widget_config_file: str
log_trash_file: str
gui_ico: str

with open(files_config_file) as f:
    lines = f.read().splitlines()
    for ln in lines:
        if _attr := search("\w+", ln):
            globals()[_attr.group()] = ROOT_DIR + "/" + sub("\w+\s*\|\s*|\s*#.*", "", ln)


class WidgetGeometryBox(AddRCMain):
    scroll_yaxis_adjust: float
    main_height: int
    main_width: int
    scrollbar_width: int

    entry_list: int
    entry_pars: int
    entry_re: int
    entry_intpair: int
    entry_int: int
    entry_codec: int
    entry_point: int
    entry_str: int
    entry_pass: int
    btn_ent_height: int
    btn_ent_entry_width: int
    lbl_ent_height: int
    lbl_ent_label_height: int

    def __init__(self):
        self._config_id = AddRCMain.__add_rc_ids__[0]
        self.main = self.Main(self)
        AddRCMain.__init__(self)

    class Main(AddRCChild):
        def __init__(self, _root_cls):
            AddRCChild.__init__(self, _root_cls)

            self.config_file = widget_config_file

            self.build_config = self.build_config
            self.source_config = self.source_config

            self.source_config(self.config_file)
            self.build_config()

        def build_config(self):
            pass


class WidgetFontBox(AddRCMain):
    _main_size: int
    _menu_size: int
    _infopop_size: int
    _attrpop_size: int
    main_font: Font
    menu_font: Font
    menu_font_bold: Font
    main_font_bold: Font
    main_font_underl: Font
    infopop_font: Font
    attrpop_font: Font

    ico_btn2_ent: PhotoImage
    ico_btn1_ent: PhotoImage

    gui_ico: PhotoImage

    width_divisor: int
    height_divisor: int

    def __init__(self):
        self._config_id = AddRCMain.__add_rc_ids__[1]
        self.main = self.Main(self)
        AddRCMain.__init__(self)

    class Main(AddRCChild):
        def __init__(self, _root_cls):
            AddRCChild.__init__(self, _root_cls)

            self.config_file = widget_config_file

            self.source_config = self.source_config
            self.build_config = self.build_config

            self.source_config(self.config_file)
            self.build_config()

        def build_config(self):
            _family = nametofont("TkFixedFont").cget("family")
            _mainkw = {'family': _family, 'size': self._main_size, 'weight': "normal", 'slant': "roman"}
            _menukw = {'family': _family, 'size': self._menu_size, 'weight': "normal", 'slant': "roman"}
            self.main_font = Font(**_mainkw)
            self.menu_font = Font(**_menukw)
            self.main_font_bold = Font(**_mainkw | {'weight': "bold"})
            self.menu_font_bold = Font(**_menukw | {'weight': "bold"})
            self.main_font_underl = Font(**_mainkw | {'underline': 1})
            self.infopop_font = Font(**{'family': _family, 'size': self._infopop_size, 'weight': "normal", 'slant': "roman"})
            self.attrpop_font = Font(**{'family': _family, 'size': self._attrpop_size, 'weight': "bold", 'slant': "roman"})
            self.gui_ico = PhotoImage(file=gui_ico)
            self.height_divisor = int(1.666666667 * self._main_size + .5)
            self.width_divisor = int(0.777777778 * self._main_size + .5)


class WidgetColorBox(AddRCMain):

    color_theme: str

    color_main_bg: str
    color_main_fg: str
    color_main_button_bg: str
    color_main_button_bg2: str
    color_main_button_fg: str
    color_main_btnact_bg: str

    color_main_text_bg: str
    color_main_text_fg: str
    color_main_text_in: str

    color_infopop_bg: str
    color_infopop_fg: str

    color_error_bg: str

    color_dir_entry_bg: str
    color_dir_entry_fg: str
    color_dir_button_bg: str
    color_dir_button_fg: str
    color_str_entry_bg: str
    color_str_entry_fg: str
    color_point_entry_bg: str
    color_point_entry_fg: str
    color_codec_entry_bg: str
    color_codec_entry_fg: str
    color_int_entry_bg: str
    color_int_entry_fg: str
    color_collect_entry_bg: str
    color_collect_entry_fg: str
    color_collect_button_bg: str
    color_collect_button_fg: str
    color_intpair_label1_bg: str
    color_intpair_label2_bg: str
    color_intpair_entry1_bg: str
    color_intpair_entry2_bg: str
    color_intpair_label1_fg: str
    color_intpair_label2_fg: str
    color_intpair_entry1_fg: str
    color_intpair_entry2_fg: str
    color_wfile_entry_bg: str
    color_wfile_entry_fg: str
    color_wfile_button_bg: str
    color_wfile_button_fg: str
    color_wfile_nul_bg: str
    color_wfile_nul_fg: str
    color_rfile_entry_bg: str
    color_rfile_entry_fg: str
    color_rfile_button_bg: str
    color_rfile_button_fg: str
    color_re_entry_bg: str
    color_re_entry_fg: str
    color_fsc_all_bg: str
    color_fsc_all_fg: str
    color_pars_entry_bg: str
    color_pars_entry_fg: str
    color_rformfile_entry_bg: str
    color_rformfile_entry_fg: str
    color_rformfile_button_bg: str
    color_rformfile_button_fg: str
    color_list_entry_bg: str
    color_list_entry_fg: str
    color_radio_bg: str
    color_radio_fg: str
    color_choice_button_bg: str
    color_choice_button_fg: str
    color_choice_entry_bg: str
    color_choice_entry_fg: str
    color_bool_bg: str
    color_bool_fg: str
    color_pass_entry_bg: str
    color_pass_entry_fg: str

    def __init__(self, color_theme=None):
        self._config_id = AddRCMain.__add_rc_ids__[2]
        self.main = self.Main(self, color_theme)
        AddRCMain.__init__(self)

    class Main(AddRCChild):
        def __init__(self, _root_cls, color_theme):
            AddRCChild.__init__(self, _root_cls)

            self.color_theme_auto_source: int = 0
            self.color_theme: str = color_theme
            self.color_themes: list = None
            self.color_zebra: int

            self.rm_choose_state: bool = False
    
            self.config_file = widget_color_table

            self.color_state = self.color_state
            self._build_associative = self._build_associative
            self._set_color = self._set_color
            self.zebra_state = self.zebra_state
            self.save_theme = self.save_theme

            self.source_config = self.source_config
            self.build_config = self.build_config

            # # # self.source_config(self.source_config)
            self.build_config()

        def build_config(self):
            with open(self.config_file) as f:
                for i in range(300):
                    ln = f.readline()
                    if search("^color_theme_auto_source\s*\|\s*[01]", ln):
                        self.color_theme_auto_source = int(search("[01]", ln).group())
                    elif not (self.color_themes and self.color_theme):
                        if _vname := search("^color_themes?\s*\|", ln):
                            if _vname.group().startswith("color_themes"):
                                color_themes = sub(f"{_vname.group()}", "", ln.strip()).split('|')
                                self.color_themes = list()
                                for theme in color_themes:
                                    theme = theme.strip()
                                    if theme != "": self.color_themes.append(theme)
                            else:
                                if self.color_theme is not None: continue
                                self.color_theme = sub(f"{_vname.group()}\|\s*|\s*#.*", "", ln.strip())
                    elif search("^color_zebra\s*\|\s*\d+", ln):
                        _i = self.color_themes.index(self.color_theme)
                        _val = sub(f"color_zebra\s*\|\s*|\s*#.*", "", ln.strip()).split('|')
                        __i = -1
                        for _v in _val:
                            _v = _v.strip()
                            if _v != "":
                                __i += 1
                                if __i == _i:
                                    self.color_zebra = int(_v)
                    else:
                        if not ln or not search("^color_", ln): continue
                        _i = self.color_themes.index(self.color_theme)
                        _attr = search("\w+", ln).group()
                        _val = sub(f"{_attr}\s*\|\s*|\s*#.*", "", ln.strip()).split('|')
                        __i = -1
                        for _v in _val:
                            _v = _v.strip()
                            if _v != "":
                                __i += 1
                                if __i == _i:
                                    setattr(self, _attr, '#' + _v)
    
            assert self.color_theme is not None or self.color_themes is not None
    
            self._build_associative()
    
        def _build_associative(self):
            def ass_hex(color: str, zebra: int):
                ass_color = "#"
                for sl in (slice(1, 3), slice(3, 5), slice(5, 7)):
                    inthex = int(color[sl], 16)
                    if (assinthex := inthex + zebra) > 255:
                        assinthex = 255
                    ass_color += ('0' + hex(assinthex).replace("0x", ""))[-2:]
                return ass_color
            self.color_main_bgz = (ass_hex(self.color_main_bg, self.color_zebra), self.color_main_bg)
            self.color_main_button_bg2 = ass_hex(self.color_main_button_bg, self.color_zebra + 10)
    
        def _set_color(self, _attr: str, _s):
            color = askcolor(getattr(self, _attr), title=_attr)
            if color[1]:
                setattr(self, _attr, color[1])
                self._build_associative()
                _s(self.color_theme)
    
        def color_state(self, widgets: list, bg: list, fg: list, setcolors, ac=None):
            if self.rm_choose_state:
                for widget, b, f in zip(widgets, bg, fg):
                    widget.unbind("<Button-1>")
                    widget.unbind("<Button-3>")
                    if ac: widget.unbind("<Button-2>")
            else:
                if ac:
                    for widget, b, f, a in zip(widgets, bg, fg, ac):
                        widget.bind("<Button-1>", lambda _, b=b, s=setcolors: self._set_color(b, s))
                        widget.bind("<Button-2>", lambda _, a=a, s=setcolors: self._set_color(a, s))
                        widget.bind("<Button-3>", lambda _, f=f, s=setcolors: self._set_color(f, s))
                else:
                    for widget, b, f in zip(widgets, bg, fg):
                        widget.bind("<Button-1>", lambda _, b=b, s=setcolors: self._set_color(b, s))
                        widget.bind("<Button-3>", lambda _, f=f, s=setcolors: self._set_color(f, s))
    
        def zebra_state(self, widget, setcolors):
            def zebra(*_):
                def _set(*_):
                    self.color_zebra = scale.get()
                    self._build_associative()
                    setcolors(self.color_theme)
                scale_window = Tk()
                scale_window.title("Zebra")
                scale_window.resizable(False, False)
                scale_window.attributes('-topmost', True)
                scale_window.focus_force()
                scale = Scale(scale_window, from_=0, to=50, orient=HORIZONTAL)
                scale.pack()
                scale.set(self.color_zebra)
                scale_window.bind("<ButtonRelease-1>", _set)
                scale_window.bind("<Return>", lambda _: scale_window.destroy())
                scale_window.bind("<Escape>", lambda _: scale_window.destroy())
                widget_close.active_windows.add(scale_window)
            if self.rm_choose_state:
                widget.unbind("<Button-2>")
            else:
                widget.bind("<Button-2>", zebra)
    
        def save_theme(self):
            _v = 0
            theme = None
            def _save(v=None):
                nonlocal _v, theme
                if v is True: _v = _v ^ 1
                else:
                    theme = entry.get()
                    save_window.destroy()
                    with open(self.config_file) as f:
                        config = f.read().splitlines()
                    with open(self.config_file, "w") as f:
                        if theme in self.color_themes:
                            _i = self.color_themes.index(theme)
                        else: _i = None
                        for ln in config:
                            if search("^color_theme", ln):
                                if _v and search("^color_theme\s", ln):
                                    f.write(sub("\|.*", "|" + (" " * 3) + theme + "\n", ln))
                                elif _i is None and search("^color_themes\s", ln):
                                    _lenprtheme = len(ln.split("|")[-1].strip())
                                    if _lenprtheme > 6:
                                        buffer = _lenprtheme - 6 + 4
                                        f.write(ln + (" " * 4) + "|" + (" " * 3) + theme + "\n")
                                    else:
                                        buffer = 4
                                        f.write(ln + (" " * (4 + 6 - _lenprtheme)) + "|" + (" " * 3) + theme + "\n")
                                else:
                                    f.write(ln + "\n")
                            elif _i is None and (cconf := search("^color_\w+", ln)):
                                f.write(ln + (" " * buffer) + "|" + (" " * 3) + str(
                                    getattr(self, cconf.group())).replace("#", "") + "\n")
                            elif _i is not None and (cconf := search("^color_\w+", ln)):
                                column = search(cconf.group() + ("\s*\|\s*[0-9a-fA-F]+" * (_i + 1)), ln).group()
                                f.write(sub(escape(column),
                                            sub("\S+$",
                                                str(getattr(self, cconf.group())).replace("#", ""),
                                                column),
                                            ln) + "\n")
                            else:
                                f.write(ln + "\n")
    
            save_window = Tk()
            save_window.title("Save theme")
            save_window.resizable(False, False)
            save_window.attributes('-topmost', True)
            entry = Entry(save_window, font=fonts.menu_font)
            check = Checkbutton(save_window, font=fonts.menu_font, text="as default", command=lambda : _save(True))
            button = Button(save_window, font=fonts.menu_font, text="Save", command=_save)
            entry.grid(row=0, column=0, columnspan=2)
            button.grid(row=1, column=0)
            check.grid(row=1, column=1)
            entry.focus_force()
            save_window.bind("<Return>", _save)
            save_window.bind("<Escape>", lambda _: save_window.destroy())
            widget_close.active_windows.add(save_window)


class WidgetStrBox(AddRCMain):
    label_none: str
    label_pwd: str
    label_str: str
    label_ireq: str
    label_disabled: str
    label_hashed: str
    label_choose: str

    errmsg_format: str
    errmsg_notfound: str
    errmsg_int: str
    errmsg_point: str
    errmsg_re: str
    errmsg_list: str
    errmsg_pars: str
    errmsg_codec: str
    errmsg_write: str
    errmsg_fsc: str
    errmsg_min_cnf: str
    errmsg_choose_state: str
    errmsg_corresponding_val: str
    errmsg_corrupted_val: str

    def __init__(self):
        self._config_id = AddRCMain.__add_rc_ids__[3]
        self.main = self.Main(self)
        AddRCMain.__init__(self)

    class Main(AddRCChild):
        def __init__(self, _root_cls):
            AddRCChild.__init__(self, _root_cls)

            self.config_file = widget_config_file

            self.source_config = self.source_config
            self.build_config = self.build_config

            self.source_config(self.config_file)
            self.build_config()

        def build_config(self):
            pass


class WidgetConfigBox(AddRCMain):
    scopes: list[str]
    main_tab_title: str

    popup_selected: str
    logcell_format: str
    cnfrow_relief:str
    cnfrow_height: int
    cnfrow_value_relief: str
    cnfrow_value_height: int
    cnfrow_value_format: str
    cnfeof_head: str
    cnfeof_text: str
    menu_bd: int
    menu_cascade_relief: str
    menu_cascade_bd: int
    tail_height_mulp: float
    tail_bd: int
    cnf_max_lines: int

    btn_ent_button_bd: int
    btn_ent_button_padx: int
    btn_ent_button_pady: int
    btn_ent_button_relief: str
    btn_ent_entry_hilith: int
    btn_ent_entry_relief: str
    ent_entry_hilith: int
    ent_entry_relief: str
    lbl_ent_label_relief: str
    lbl_ent_entry_relief: str

    tag_header: dict
    tag_chapter: dict
    tag_section: dict
    tag_attr: dict

    tag_script: dict
    tag_subcap: dict
    tag_path: dict
    tag_key: dict
    tag_input: dict
    tag_menu: dict
    tag_button: dict
    tag_call: dict
    tag_st: dict
    tag_py: dict
    tag_example: dict

    index_tag_units: str
    index_tag_types: str
    index_tag_scopes: str

    all_sc_re: Pattern
    cnf_units_mins: dict[str: Pattern]
    cnf_units_re: Pattern
    cnf_types_cnf_re: Pattern
    cnf_ln_re: Pattern
    universal_re: Pattern
    scopes_re: Pattern
    cnf_type_re: Pattern

    def __init__(self):
        self._config_id = AddRCMain.__add_rc_ids__[4]
        self.main = self.Main(self)
        AddRCMain.__init__(self)

    class Main(AddRCChild):
        def __init__(self, _root_cls):
            AddRCChild.__init__(self, _root_cls)

            self.config_file = widget_config_file

            self.build_config = self.build_config
            self.source_config = self.source_config

            self.source_config(self.config_file)
            self.build_config()

        def build_config(self):

            with open(configuration_sheet.__file__) as f: f = f.read()
            cnfunits = search(f"(?<=\$\$\${self.index_tag_units})(.|\n)*(?={self.index_tag_units}\$\$\$)", f).group().split('#')
            cnftypes = search(f"(?<=\$\$\${self.index_tag_types})(.|\n)*(?={self.index_tag_types}\$\$\$)", f).group().split('#')
            self.scopes = [i.strip() for i in search(f"(?<=\$\$\${self.index_tag_scopes})(.|\n)*(?={self.index_tag_scopes}\$\$\$)", f).group().split('#')
                           if i.strip()]

            self.all_sc_re = "[0" + str().join(["%d" % i for i in range(1, len(self.scopes) + 1)]) + "]"

            self.cnf_units_mins = dict()
            self.cnf_units_re = "("

            for unit_ln in cnfunits:
                if not (_unit := search("\w+", unit_ln)):
                    continue
                unit = _unit.group()
                self.cnf_units_mins[unit] = sub(f"{unit}\s*|\$\[|]", "", unit_ln).split()
                self.cnf_units_re += unit + "|"

            self.cnf_units_re = self.cnf_units_re[:-1] + ")"

            self.cnf_types_cnf_re = dict()
            self.cnf_ln_re = ""

            for _type in cnftypes:
                if not (_type := _type.strip()):
                    continue
                self.cnf_ln_re += _type + "|"
                self.cnf_types_cnf_re[
                    _type
                ] = compile("(?<=" + self.all_sc_re + "\$" + _type + ";\{).*(?=}\$$)")

            self.cnf_ln_re = compile(
                f"\s{self.cnf_units_re}\${self.all_sc_re}\$({self.cnf_ln_re[:-1]})"
            )

            self.universal_re = compile(
                f"\s"
                f"{self.cnf_units_re}\$0\$"
            )

            self.scopes_re = {
                scope: compile(
                    f"\s{self.cnf_units_re}\${n + 1}\$"
                ) for n, scope in enumerate(self.scopes)
            }

            self.cnf_type_re = compile(
                f"(?<=\${self.all_sc_re}\$)\w+(?=;|$)"
            )

try:
    fonts = WidgetFontBox()
    colors = WidgetColorBox()
    strings = WidgetStrBox()
    geo = WidgetGeometryBox()
    configs = WidgetConfigBox()
except RuntimeError:
    pass
