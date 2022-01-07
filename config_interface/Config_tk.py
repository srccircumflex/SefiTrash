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

from tkinter import DISABLED

from config_interface import ROOT_TK, MOD_DEBUG
from config_interface._rc import _run as CRC
from config_interface.prc.config_main_tab import CnfMainTab
from config_interface.sec.auto_close import widget_close
from config_interface.sec.tab_ctl import TAB_CTL
from config_interface.wdg.menus import PopUpMenu, TopMenu, MenuCascade, MenuCheckB, MenuInfoCascade

ROOT_TK.resizable(False, False)
ROOT_TK.iconphoto(True, CRC.fonts.gui_ico)

class CnfGUI:
    def __init__(self):

        self.mainloop = ROOT_TK.mainloop

        self.MAIN_TAB = CnfMainTab(ROOT_TK)

        self._search_additional_tabs()

        self.TopMenuBar = TopMenu(ROOT_TK)

        for scope in CRC.configs.scopes:
            MenuCheckB(self.TopMenuBar,
                           scope,
                           lambda _sc=scope: self.switch_scope(_sc))

        self.TopMenuBar.add_cascade(label="|", state=DISABLED, font=CRC.fonts.menu_font)

        self.MenuCascadeValues = MenuCascade(self.TopMenuBar,
                                                 "Values",
                                                 ("Fill", "None", "Defaults", None, "Consume"),
                                                 (self.MAIN_TAB.filldefaults,
                                                  self.MAIN_TAB.setnone,
                                                  self.MAIN_TAB.setdefaults,
                                                  None,
                                                  self.MAIN_TAB.consume))

        self.MenuCascadeFile = MenuCascade(self.TopMenuBar,
                                               "File",
                                               ("Source", "Fill", None, "Write"),
                                               (self.MAIN_TAB.sourcefile,
                                                self.MAIN_TAB.fillfile,
                                                None,
                                                self.MAIN_TAB.savefile))

        self.TopMenuBar.add_cascade(label="|", state=DISABLED, font=CRC.fonts.menu_font)

        self.MenuCascadeHelp = MenuInfoCascade(self.TopMenuBar,
                                               self.MAIN_TAB.txtCell.text)

        if MOD_DEBUG:
            self._color_popup()

        for w in (self.TopMenuBar, self.MAIN_TAB.footerFrameR, self.MAIN_TAB.footerFrameL):
            widget_close.bind(w)

        if CRC.colors.color_theme_auto_source: self.setcolors(CRC.colors.color_theme)

        ROOT_TK.bind("<Control-f>", lambda _: self.MAIN_TAB.filldefaults())
        ROOT_TK.bind("<Control-c>", lambda _: self.MAIN_TAB.consume())
        ROOT_TK.bind("<Control-s>", lambda _: self.MAIN_TAB.savefile())
        self.MenuCascadeFile.bind("<Enter>", lambda _:self.MenuCascadeFile.after(1000, self.MenuCascadeFile.unpost))

    def switch_scope(self, update_):
        self.MAIN_TAB._switch_scope(update_)
        self.setcolors(CRC.colors.color_theme)
        self.MAIN_TAB.footerFrameL.update_text({update_: self.MAIN_TAB.scopes[update_]})
        self._search_additional_tabs()

    def _search_additional_tabs(self):
        from config_interface.tab_plugins import ADD_TABS

        add_tabs = ADD_TABS.copy()
        for add_attr in ADD_TABS.copy():
            if self.MAIN_TAB.cnf_units.get(add_attr.TARGET_UNIT):
                if self.MAIN_TAB.cnf_units.get(add_attr.TARGET_UNIT).get(add_attr.TARGET_ATTR):
                    add_tabs.remove(add_attr)
                    if add_attr.TARGET_ATTR in TAB_CTL.additional_tabs:
                        TAB_CTL.show_(add_attr)
                    else:
                        add_attr.Main.__call__(self, TAB_CTL.expand(add_attr))

        for hide_tab in add_tabs:
            try:
                TAB_CTL.hide_(hide_tab)
            except ValueError:
                pass

    def _color_popup(self):
        PopUpMenu(ROOT_TK,
                  ["Choosing", None] + CRC.colors['main'].color_themes,
                  [
                      self.choosecolorstate, None
                  ] + [
                      lambda t=theme: self.setcolors(t) for theme in CRC.colors['main'].color_themes
                  ],
                  (self.TopMenuBar, self.MAIN_TAB.footerFrameR, self.MAIN_TAB.footerFrameL),
                  i_is_radio=[i + 2 for i in range(len(CRC.colors['main'].color_themes))])

    def setcolors(self, theme):
        if theme != CRC.strings['main'].label_choose and theme != CRC.colors['main'].color_theme:
            CRC.colors = CRC.WidgetColorBox(theme)
        for unit in self.MAIN_TAB.cnf_units:
            for row in self.MAIN_TAB.cnf_units[unit]:
                self.MAIN_TAB.cnf_units[unit][row].setcolor()
                self.MAIN_TAB.cnf_units[unit][row].cnf.setcolor()
        self.MAIN_TAB.footerFrameR.update_text("theme", theme)
        self.MAIN_TAB.CellLeft.setcolor()
        self.MAIN_TAB.CellRight.setcolor()
        self.MAIN_TAB.txtCell.setcolor()
        self.MAIN_TAB.footerFrameL.setcolor()
        self.MAIN_TAB.footerFrameR.setcolor()
        self.MAIN_TAB.eof.setcolor()
        self.TopMenuBar.setcolor()
        self.MenuCascadeValues.setcolor()
        self.MenuCascadeFile.setcolor()
        self.MenuCascadeHelp.setcolor()

    def save_theme(self):
        CRC.colors['main'].save_theme()

    def choosecolorstate(self):
        if not CRC.colors['main'].rm_choose_state:
            CRC.colors['main'].color_theme = CRC.strings['main'].label_choose
            self.MenuCascadeHelp.insert_info("!Color")
            PopUpMenu(ROOT_TK,
                      ["Leave", None, "Save as"],
                      [self.choosecolorstate, None, self.save_theme],
                      (self.TopMenuBar, self.MAIN_TAB.footerFrameR, self.MAIN_TAB.footerFrameL),
                      )
        else:
            self._color_popup()
        self.MAIN_TAB.choosecolor(self.setcolors)
        CRC.colors['main'].zebra_state(self.MAIN_TAB.CellLeft.scrollbar_y, self.setcolors)
        self.setcolors(CRC.colors['main'].color_theme)
        CRC.colors['main'].rm_choose_state = CRC.colors['main'].rm_choose_state ^ True


def main():
    CnfGUI().mainloop()
