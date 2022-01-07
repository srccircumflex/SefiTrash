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


from tkinter import Menu, LabelFrame, Text
from tkinter import LEFT, DISABLED, NORMAL, EW, END
from re import compile

from config_interface._rc import _run as CRC
from config_interface.sec.auto_close import widget_close
from config_interface.sec.doc_reader import get_all_keys, gen_infolines
from config_interface.wdg.tools import MenuCascade as _MenuCascade, PopUpMenu as _PopUpMenu, TextHighlighting


class TopMenu(Menu):
    def __init__(self, master):
        Menu.__init__(
            self,
            master,
            bd=CRC.configs.menu_bd
        )
        master.config(menu=self)

    def setcolor(self):
        self.config(fg=CRC.colors.color_main_button_fg, bg=CRC.colors.color_main_button_bg,
                    activebackground=CRC.colors.color_main_btnact_bg)


class MenuCascade(_MenuCascade):
    def __init__(self,
                 master: Menu,
                 casc_label: str,
                 labels: [list, tuple],
                 commands: [list, tuple],
                 i_is_radio: [list, tuple] = (),
                 i_is_check: [list, tuple] = ()
                 ):

        _MenuCascade.__init__(
            self, master, casc_label, labels, commands, i_is_radio, i_is_check,
            casctop_kwargs={'font': CRC.fonts.menu_font},
            casc_kwargs={'bd': CRC.configs.menu_cascade_bd, 'relief': CRC.configs.menu_cascade_relief},
            check_kwargs={'font': CRC.fonts.menu_font, 'selectcolor': CRC.colors.color_main_button_fg},
            radio_kwargs={'font': CRC.fonts.menu_font, 'selectcolor': CRC.colors.color_main_button_fg},
            button_kwargs={'font': CRC.fonts.menu_font}
        )

    def setcolor(self):
        self.config(fg=CRC.colors.color_main_button_fg, bg=CRC.colors.color_main_button_bg,
                    activebackground=CRC.colors.color_main_btnact_bg)


class MenuInfoCascade(_MenuCascade, Menu):
    def __init__(self,
                 master: Menu,
                 text: Text
                 ):

        self.text = text

        kws = get_all_keys(CRC.gui_info_file)

        first = False
        if kws:
            first = kws[0]

            for kw in kws.copy():
                if kw[0] == '!':
                    kws.remove(kw)

        if kws:

            _MenuCascade.__init__(
                self, master, 'Info', list(kws), [lambda kw=kw: self.insert_info(kw) for kw in kws],
                casctop_kwargs={'font': CRC.fonts.menu_font},
                casc_kwargs={'bd': CRC.configs.menu_cascade_bd, 'relief': CRC.configs.menu_cascade_relief},
                button_kwargs={'font': CRC.fonts.menu_font}
            )

        else:
            Menu.__init__(self)

        if first:
            self.insert_info(first)

    def insert_info(self, kw):
        _state = self.text.cget("state")
        self.text.config(state=NORMAL)
        self.text.delete("1.0", END)
        self.text.insert("1.0", str().join(gen_infolines(kw, CRC.gui_info_file)))
        TextHighlighting(
            self.text,
            main_config={
                compile("`[A-Z0-1_*]+'"): {
                                         'font': CRC.fonts.main_font_bold
                                     } | CRC.configs.tag_attr,
                compile("`[^`']+\.py'"): {
                                         'font': CRC.fonts.main_font_bold
                                     } | CRC.configs.tag_script,
                compile('"[^"]+"'): {
                                        'font': CRC.fonts.main_font
                                    } | CRC.configs.tag_path,
                compile("<[^<>]+>"): {
                                         'font': CRC.fonts.main_font
                                     } | CRC.configs.tag_key,
                compile("`[^`']+`"): {
                                         'font': CRC.fonts.main_font
                                     } | CRC.configs.tag_input,
                compile("\[\w+]"): {
                                       'font': CRC.fonts.main_font_bold
                                   } | CRC.configs.tag_menu,
                compile("-[a-zA-Z]+-"): {
                                      'font': CRC.fonts.main_font_bold
                                  } | CRC.configs.tag_button,
                compile("\w+\(\)"): {
                                        'font': CRC.fonts.main_font
                                    } | CRC.configs.tag_call,
                compile("\w+@\w+\.com"): {
                                        'font': CRC.fonts.main_font
                                    } | CRC.configs.tag_call,
                compile("SefiTrash"): {
                                          'font': CRC.fonts.main_font_bold
                                      } | CRC.configs.tag_st,
                compile("\.py"): {
                                     'font': CRC.fonts.main_font
                                 } | CRC.configs.tag_py,
                compile("(?<=^\t)\S.*"): {
                                             'font': CRC.fonts.main_font_underl
                                         } | CRC.configs.tag_subcap,
                compile("(?<=^\t\s\s)\S.*"): {
                                             'font': CRC.fonts.main_font_bold
                                         } | CRC.configs.tag_example,
                compile("^\w.*"): {
                                      'font': CRC.fonts.main_font_bold
                                  } | CRC.configs.tag_chapter,
            },
            first_clause={
                compile("\s{6}\S.+\s{6}"): {
                                             'font': CRC.fonts.main_font_underl
                                         } | CRC.configs.tag_header
            }
        ).highlight()
        self.text.config(state=_state)

    def setcolor(self):
        self.config(fg=CRC.colors.color_main_button_fg, bg=CRC.colors.color_main_button_bg,
                    activebackground=CRC.colors.color_main_btnact_bg)


class MenuCheckB:
    def __init__(self,
                 master: Menu,
                 label: str,
                 command
                 ):
        master.add_checkbutton(
            label=label,
            command=command,
            compound=LEFT,
            font=CRC.fonts.menu_font,
            selectcolor=CRC.colors.color_main_button_fg
        )


class PopUpMenu(_PopUpMenu):
    def __init__(self,
                 master,
                 labels: [list, tuple],
                 commands: [list, tuple],
                 bind_up: [list, tuple] = (),
                 i_is_radio: [list, tuple] = (),
                 i_is_check: [list, tuple] = ()
                 ):
        _PopUpMenu.__init__(
            self, master, labels, commands, bind_up, i_is_radio, i_is_check,
            button_kwargs={'font': CRC.fonts.menu_font},
            check_kwargs={'font': CRC.fonts.menu_font, 'selectcolor': CRC.configs.popup_selected},
            radio_kwargs={'font': CRC.fonts.menu_font, 'selectcolor': CRC.configs.popup_selected},
        )

    def popup(self, event):
        try:
            widget_close.active_windows.add(self)
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class FooterLine:
    class Left(LabelFrame):
        def __init__(self, master, row, column):
            self.tail_scope_switches = {_sc: "[0\\ ]" for _sc in CRC.configs.scopes}
            self.tail_scope_bits = {True: "[ /1]", False: "[0\\ ]"}
            self.tail_scope_line = "[    ]    CNF_SCOPE: Universal [ /1]" + str(

            ).join([f"    |    {_sc} %({_sc})s" for _sc in CRC.configs.scopes])
            LabelFrame.__init__(
                self,
                master,
                font=CRC.fonts.menu_font_bold,
                width=CRC.geo.main_width + CRC.geo.scrollbar_width,
                height=int(CRC.fonts._menu_size * CRC.configs.tail_height_mulp),
                bd=CRC.configs.tail_bd
            )
            self.grid(row=row, column=column, sticky=EW)

        def setcolor(self):
            self.config(bg=CRC.colors.color_main_button_bg, fg=CRC.colors.color_main_button_fg)

        def update_text(self, update_: dict):
            for scope, bool_val in zip(update_.keys(), update_.values()):
                self.tail_scope_switches[scope] = self.tail_scope_bits[bool_val]
            self.config(
                text=(self.tail_scope_line % self.tail_scope_switches)
            )

    class Right(LabelFrame):
        def __init__(self, master, row, column):
            global footerFrameR
            self.tail_state_switches = {
                "theme": "????????????",
                "state": "[    / OFF ]",
                "clear": "[ ON \\     ]"
            }
            self.tail_autoclear_bits = {True: "[ ON \\     ]", False: "[    / OFF ]"}
            self.tail_state_bits = {NORMAL: "[ r+ \\     ]", DISABLED: "[    / OFF ]"}

            self.tail_state_line = "|    Theme : %(theme)-12s    " \
                                   "|    TextCellState %(state)s    " \
                                   "|    TextCellAutoClear %(clear)s    |"

            LabelFrame.__init__(
                self,
                master,
                font=CRC.fonts.menu_font_bold,
                width=CRC.geo.main_width + CRC.geo.scrollbar_width,
                height=int(CRC.fonts._menu_size * CRC.configs.tail_height_mulp),
                bd=CRC.configs.tail_bd
            )
            self.grid(row=row, column=column, sticky=EW)

            footerFrameR = self

        def setcolor(self):
            self.config(bg=CRC.colors.color_main_button_bg, fg=CRC.colors.color_main_button_fg)

        def update_text(self, _key, _val):
            self.tail_state_switches[_key] = _val
            self.config(
                text=self.tail_state_line % self.tail_state_switches
            )

footerFrameR = None

