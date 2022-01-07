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

from tkinter.ttk import Notebook, Style
from tkinter import Frame

from config_interface import ROOT_TK
from config_interface._rc import _run as CRC


class TabCtl(Notebook):
    style = Style()
    style.configure('TNotebook.Tab', font=CRC.fonts.menu_font_bold)

    def __init__(self):
        Notebook.__init__(self, ROOT_TK)
        self.pack()

        self.MAIN_TAB = Frame(ROOT_TK)
        self.add(self.MAIN_TAB, text=CRC.configs.main_tab_title)

        self.additional_tabs = dict()

        self.bind("<Button-1>", self.update_tabs_)

    def update_tabs_(self, *_):
        for tab_name in self.additional_tabs:
            self.additional_tabs[tab_name][1].INST.update()

    def expand(self, add_tab):
        _frame = Frame(ROOT_TK)
        self.add(_frame, text=add_tab.TARGET_LABEL)
        self.additional_tabs[add_tab.TARGET_ATTR] = (_frame, add_tab)
        return _frame

    def hide_(self, tab):
        self.hide(list(self.additional_tabs).index(tab.TARGET_ATTR) + 1)

    def show_(self, tab):
        self.add(self.additional_tabs[tab.TARGET_ATTR][0], text=tab.TARGET_LABEL)


TAB_CTL = TabCtl()
