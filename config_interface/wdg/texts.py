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


from tkinter import Text
from tkinter import DISABLED, NSEW, NORMAL, END
from re import sub, compile
from config_interface._rc import _run as CRC

from config_interface.wdg import menus
from config_interface.sec.auto_close import widget_close
from config_interface.sec.doc_reader import gen_infolines
from config_interface.wdg.tools import TextHighlighting


class TextCell:

    def __init__(self, master):
        global txtCell
        self.master = master
        self.text = Text(
            master,
            font=CRC.fonts.main_font,
            width=CRC.geo.main_width // CRC.fonts.width_divisor,
            height=CRC.geo.main_height
        )
        self.text.config(state=DISABLED)
        self.text.grid(sticky=NSEW)
        self.formstr = CRC.configs.logcell_format + "\n"

        self.clipboard = str()
        self._state = DISABLED
        self._autoclear = True
        self._unit = str()

        txtCell = self

        self.master = master

    def setcolor(self):
        self.text.config(bg=CRC.colors.color_main_text_bg, fg=CRC.colors.color_main_text_fg,
                         insertbackground=CRC.colors.color_main_text_in)

    def add_wiki_attr(self, __w, name: str):
        __w.bind("<Button-1>", lambda _, s=self, n=name: s._wiki(n))

    def _wiki(self, _attr):
        self.master.cell.yview_scroll(-200, "pages")
        widget_close.upost()
        self.delete()
        self.text.config(state=NORMAL)
        _g = gen_infolines(_attr)
        while True:
            try:
                self.text.insert("1.0", next(_g))
            except StopIteration:
                TextHighlighting(
                    self.text,
                    main_config={
                        compile("^\w.*"): {
                                              'font': CRC.fonts.main_font_bold
                                          } | CRC.configs.tag_chapter,
                        compile("^\["): {
                                            'font': CRC.fonts.main_font_bold
                                        } | CRC.configs.tag_section,
                        compile("`[^']+'"): {
                                                'font': CRC.fonts.main_font_bold
                                            } | CRC.configs.tag_attr
                    },
                    first_clause={
                        compile("\S+..."): {
                                               'font': CRC.fonts.main_font_underl
                                           } | CRC.configs.tag_header
                    }
                ).highlight()
                break
        self.text.config(state=self._state)

    def delete(self):
        if not self._autoclear: return
        self.text.config(state=NORMAL)
        with open(CRC.log_trash_file, "w") as f:
            f.write(self.text.get("1.0", END))
        self.text.delete("1.0", END)
        self.text.config(state=self._state)

    def insert(self, *args, _str=""):
        self.text.config(state=NORMAL)
        self.text.insert("1.0", sub("\\\\n", "\n", _str) + sub("\\\\n", "\n", (self.formstr % args if args else "")))
        self.text.config(state=self._state)

    def unit_append(self, *args, _str=""):
        self._unit += sub("\\\\n", "\n", _str) + sub("\\\\n", "\n", (self.formstr % args if args else ""))

    def unit_flush(self):
        self.text.config(state=NORMAL)
        self.text.insert("1.0", self._unit)
        self._unit = str()
        self.text.config(state=self._state)

    def clipboard_insert(self):
        self.text.config(state=NORMAL)
        with open(CRC.log_trash_file, "r") as f:
            self.text.insert("1.0", f"{'=' * 98}\n{f.read()}\n{'=' * 98}\n")
        self.text.config(state=self._state)

    def state(self):
        self._state = (NORMAL if self._state == DISABLED else DISABLED)
        self.text.config(state=self._state)
        menus.footerFrameR.update_text("state", menus.footerFrameR.tail_state_bits[self._state])

    def flush(self):
        self.text.config(state=NORMAL)
        self.text.delete("1.0", END)
        self.text.config(state=self._state)

    def autoclear(self):
        self._autoclear = self._autoclear ^ True
        menus.footerFrameR.update_text("clear", menus.footerFrameR.tail_autoclear_bits[self._autoclear])

    def choosecolor(self, setmeth):
        CRC.colors.color_state([self.text],
                               ['color_main_text_bg'],
                               ['color_main_text_fg'],
                               setmeth,
                               ['color_main_text_in'])


txtCell: TextCell = None
