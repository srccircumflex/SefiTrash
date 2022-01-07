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

from tkinter import LabelFrame, Canvas, Scrollbar, Frame, Pack, Grid, Place

from typing import Literal


v_EVENTS = ("<Button-4>", "<Button-5>", "<MouseWheel>")
V_EVENTS = ("<Next>", "<Prior>")
h_EVENTS = ("<Control-Button-4>", "<Control-Button-5>", "<Control-MouseWheel>")
H_EVENTS = ("<Control-Right>", "<Control-Left>")

FACTORIZING_KEYSYM = ("Down", "Up", "Next", "Prior", "Right", "Left")
INVERT_KEYSYM = ("Down", "Right", "Next")


class ScrollCell(Frame):

    def __init__(self,
                 master,
                 reverse_scroll: bool = True,
                 VH_factors: tuple = (6, 8),
                 cell_kwargs: dict = None,
                 scrollbar_y_kwargs: dict = None,
                 scrollbar_x_kwargs: dict = None,
                 orient_gr_width: Literal["sum", "widget", ""] = False,
                 orient_gr_height: Literal["sum", "widget", ""] = False,
                 auto_bind_mod: Literal["v", "h", "V", "H", "vh", "vH", "Vh", "VH", ""] = None,
                 **_front_kwargs):

        self.v_EVENTS = v_EVENTS
        self.V_EVENTS = V_EVENTS
        self.h_EVENTS = h_EVENTS
        self.H_EVENTS = H_EVENTS

        self.FACTORIZING_KEYSYM = FACTORIZING_KEYSYM
        self.INVERT_KEYSYM = INVERT_KEYSYM

        self.trend: int = (-1 if reverse_scroll else 1)
        self.VH_factors: tuple = VH_factors

        if cell_kwargs is None:
            cell_kwargs = dict()

        if scrollbar_y_kwargs is None and scrollbar_x_kwargs is None:
            scrollbar_y_kwargs = dict()

        self.orient_gr_width = orient_gr_width
        self.orient_gr_height = orient_gr_height
        self.auto_bind_mod = auto_bind_mod

        #

        self._container = LabelFrame(master)

        _scrollcommands = {}

        if isinstance(scrollbar_x_kwargs, dict):
            self.scrollbar_x = Scrollbar(self._container,
                                         orient="horizontal",
                                         **scrollbar_x_kwargs)
            self.scrollbar_x.pack(side="bottom", fill="x")

            _scrollcommands |= {'xscrollcommand': self.scrollbar_x.set}

        if isinstance(scrollbar_y_kwargs, dict):
            self.scrollbar_y = Scrollbar(self._container,
                                         orient="vertical",
                                         **scrollbar_y_kwargs)
            self.scrollbar_y.pack(side="right", fill="y")

            _scrollcommands |= {'yscrollcommand': self.scrollbar_y.set}

        self.cell = Canvas(self._container, **cell_kwargs)
        self.cell.pack(side="right")

        Frame.__init__(self, self.cell, **_front_kwargs)

        self.cell.create_window((0, 0),
                                window=self,
                                anchor="nw")

        #

        self.cell.config(_scrollcommands)

        if isinstance(scrollbar_x_kwargs, dict):
            self.scrollbar_x.config(command=self.cell.xview)
        if isinstance(scrollbar_y_kwargs, dict):
            self.scrollbar_y.config(command=self.cell.yview)

        self.cell.bind('<Configure>', self._update_scroll)
        self.bind('<Configure>', self._update_scroll)
        self.bind('<Expose>', self.__expose)

        m = (auto_bind_mod if auto_bind_mod else "v")
        self.scroll_update(self.cell, m)
        self.scroll_update(self, m)

        for geo_meth in Pack.__dict__.keys() | Grid.__dict__.keys() | Place.__dict__.keys():
            if not geo_meth.startswith('_') and geo_meth != 'config' and geo_meth != 'configure':
                setattr(self, geo_meth, getattr(self._container, geo_meth))

    def __orient_gr_width(self, *_):
        def width():
            return {
                "sum": self.winfo_width,
                "widget": max(self.winfo_children(), key=lambda w: w.winfo_width()).winfo_width
            }[self.orient_gr_width]()

        self.config_cell(
            width=width()
        )

    def __orient_gr_height(self, *_):
        def height():
            return {
                "sum": self.winfo_height,
                "widget": max(self.winfo_children(), key=lambda w: w.winfo_height()).winfo_height
            }[self.orient_gr_width]()

        self.config_cell(
            height=height()
        )

    def __expose(self, *_):
        if self.orient_gr_width:
            self.__orient_gr_width()
        if self.orient_gr_height:
            self.__orient_gr_height()
        if self.auto_bind_mod:
            for w in self.winfo_children():
                self.scroll_update(w, self.auto_bind_mod)

    def __scroll_val(self, e) -> int:
        u = self.trend
        if e.num == 5 or e.delta < 0 or e.keysym in self.INVERT_KEYSYM: u = ~ u + 1
        if e.keysym in self.FACTORIZING_KEYSYM: u *= self.VH_factors[0]
        return u

    def _scroll_x(self, e):
        self.scroll_x(self.__scroll_val(e))

    def _scroll_y(self, e):
        self.scroll_y(self.__scroll_val(e))

    def scroll_x(self, z: int):
        self.cell.xview_scroll(z, "units")

    def scroll_y(self, z: int):
        self.cell.yview_scroll(z, "units")

    def scroll_update(self, __add_w, bind_mod: Literal["v", "h", "V", "H", "vh", "vH", "Vh", "VH"] = "v"):
        vert = {event: self._scroll_y for event in self.v_EVENTS}
        VERT = vert | {event: self._scroll_y for event in self.V_EVENTS}
        hori = {event: self._scroll_x for event in self.h_EVENTS}
        HORI = hori | {event: self._scroll_x for event in self.H_EVENTS}
        _mod = {
            "v": vert,
            "h": hori,
            "V": VERT,
            "H": HORI,
            "vh": vert | hori,
            "vH": vert | HORI,
            "Vh": VERT | hori,
            "VH": VERT | HORI
        }
        for binding in _mod[bind_mod].items():
            __add_w.bind(*binding)

    def _update_scroll(self, *_):
        self.cell.update_idletasks()
        self.cell.config(scrollregion=self.cell.bbox("all"))

    def config_container(self, **kwargs):
        self._container.config(kwargs)

    def config_cell(self, **kwargs):
        self.cell.config(kwargs)

    def config_scrollbar(self, **kwargs):
        self.scrollbar_y.config(kwargs)
