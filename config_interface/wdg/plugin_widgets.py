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


from config_interface.wdg.ScrollCell import ScrollCell as _ScrollCell

from tkinter import Text
from tkinter import DISABLED, NORMAL, END

from re import sub

from config_interface._rc import _run as CRC


class ScrollCell(_ScrollCell):
    def __init__(self,
                 master,
                 configKey,
                 cell_kwargs,
                 scrollbar_kwargs,
                 **_front_kwargs):

        _ScrollCell.__init__(self, master, cell_kwargs=cell_kwargs, scrollbar_y_kwargs=scrollbar_kwargs, **_front_kwargs)
        self.configKey = configKey

    def setcolor(self):
        self.config_container(bg=CRC.colors[self.configKey].color_main_bg)
        self.config_cell(bg=CRC.colors[self.configKey].color_main_bg)
        self.config_scrollbar(bg=CRC.colors[self.configKey].color_main_button_bg2,
                          activebackground=CRC.colors[self.configKey].color_main_btnact_bg)
        self.config(bg=CRC.colors[self.configKey].color_main_bg)

    def choosecolor(self, setmeth):
        CRC.colors[self.configKey].color_state([self.scrollbar_y],
                                               ['color_main_button_bg'],
                                               ['color_main_button_fg'],
                                               setmeth,
                                               ac=['color_main_btnact_bg'])


class TextCell:
    def __init__(self,
                 master,
                 configKey,
                 **grid_kwargs):
        self.master = master
        self.configKey = configKey
        self.text = Text(
            master,
            width=1,
            font=CRC.fonts.main_font,
        )
        self.text.config(state=DISABLED)
        self.text.grid(**grid_kwargs)
        self.formstr = CRC.configs[configKey].logcell_format + "\n"

        self.clipboard = str()
        self._state = DISABLED
        self._autoclear = True
        self._unit = str()

    def setcolor(self):
        self.text.config(bg=CRC.colors[self.configKey].color_main_bg, fg=CRC.colors[self.configKey].color_main_fg,
                         insertbackground=CRC.colors[self.configKey].color_error_bg)

    def delete(self):
        self.text.config(state=NORMAL)
        self.text.delete("1.0", END)
        self.text.config(state=self._state)

    def insert(self, *args, _str=""):
        """

        :param args: '%s%s' % args
        :param _str:
        :return:
        """
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

