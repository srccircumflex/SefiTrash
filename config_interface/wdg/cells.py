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


from config_interface._rc import _run as CRC
from config_interface.wdg.ScrollCell import ScrollCell as _ScrollCell
from config_interface.sec.auto_close import widget_close


class ScrollCell(_ScrollCell):
    def __init__(self, master):

        _ScrollCell.__init__(self,
                             master,
                             cell_kwargs={'height': CRC.geo.main_height,
                                         'width': CRC.geo.main_width},
                             scrollbar_y_kwargs={'width': CRC.geo.scrollbar_width})

    def _scroll_y(self, e):
        widget_close.upost()
        self.scroll_y(self.__scroll_val(e))

    def setcolor(self):
        self.config_container(bg=CRC.colors.color_main_bg)
        self.config_cell(bg=CRC.colors.color_main_bg)
        self.config_scrollbar(bg=CRC.colors.color_main_button_bg2, activebackground=CRC.colors.color_main_btnact_bg)
        self.config(bg=CRC.colors.color_main_bg)

    def choosecolor(self, setmeth):
        CRC.colors.color_state([self.scrollbar_y],
                               ['color_main_button_bg'],
                               ['color_main_button_fg'],
                               setmeth,
                               ac=['color_main_btnact_bg'])

