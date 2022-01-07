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


from re import search

from tkinter import Label, LabelFrame
from tkinter import W, X, EW

from config_interface._rc import _run as CRC
from config_interface.prc import configtypeobjs as COJ
from config_interface.wdg import texts


class CnfRow(Label):
    zebras = dict()

    def __init__(self, master, _attr_name: str, _cnf_ln: str):
        self.unit = search(f"(?<=\s){CRC.configs.cnf_units_re}(?=\$)", _cnf_ln).group()
        self.zebras.setdefault(self.unit, 0)

        _type = search(CRC.configs.cnf_type_re, _cnf_ln).group()
        assert hasattr(COJ, _type := 'type_' + _type), _type

        Label.__init__(self,
                       master,
                       relief=CRC.configs.cnfrow_relief,
                       height=CRC.configs.cnfrow_height)
        self.label = Label(self,
                           relief=CRC.configs.cnfrow_value_relief,
                           height=CRC.configs.cnfrow_value_height,
                           text=CRC.configs.cnfrow_value_format % _attr_name,
                           font=CRC.fonts.main_font)
        self.label.grid(sticky=W, column=0)

        self.cnf = getattr(COJ, _type).__call__(self, _attr_name, _cnf_ln, "main", texts.txtCell)

    def forget(self):
        self.label.grid_forget()

    def setcolor(self):
        self.zebras[self.unit] = self.zebras[self.unit] ^ 1
        self.config(bg=CRC.colors.color_main_bgz[self.zebras[self.unit]])
        self.label.config(bg=CRC.colors.color_main_bgz[self.zebras[self.unit]], fg=CRC.colors.color_main_fg)


class SectorFrame(LabelFrame):

    def __init__(self, master, name: str):
        LabelFrame.__init__(self, master, width=CRC.geo.main_width * 2)
        self.label = Label(
            self,
            text=" [ %s ]" % name,
            font=CRC.fonts.main_font,
            width=CRC.geo.main_width // CRC.fonts.width_divisor
        )
        self.label.pack(fill=X)

    def forget(self):
        self.label.pack_forget()

    def setcolor(self):
        self.config(bg=CRC.colors.color_main_bg)


class EOF:
    def __init__(self, master):
        self.frame = LabelFrame(master)
        self.ulabel = Label(self.frame,
                            text="- %s -" % CRC.configs.cnfeof_head,
                            font=CRC.fonts.main_font)
        self.ulabel.pack(fill=X)
        self.rlabel = Label(self.frame,
                            relief="flat",
                            height=1,
                            text=CRC.configs.cnfeof_text,
                            font=CRC.fonts.main_font)
        self.rlabel.pack()
        self.frame.grid(sticky=EW)

    def forget(self):
        self.rlabel.pack_forget()
        self.ulabel.pack_forget()
        self.frame.grid_forget()

    def setcolor(self):
        self.frame.config(bg=CRC.colors.color_main_bg)
        self.rlabel.config(bg=CRC.colors.color_main_bg, fg=CRC.colors.color_main_fg)
