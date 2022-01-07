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

from tkinter import W, X, EW
from tkinter.filedialog import askopenfilename, asksaveasfilename

from re import search, sub
from ast import literal_eval

from config_interface import ENCODING, DefIfEndIf, IFDEFENDIF, default_values, configuration_sheet, value_name2default_name, default_name2value_name, value_name_re,  ROOT_TK, MOD_DEBUG
from config_interface._rc import _run as CRC
from config_interface.sec.tab_ctl import TAB_CTL
from config_interface.sec.auto_close import widget_close
from config_interface.sec.doc_reader import get_infopop_lines
from config_interface.wdg import texts
from config_interface.wdg.InfoPopUp import InfoPopUp
from config_interface.wdg.rows import CnfRow, EOF, SectorFrame
from config_interface.wdg.ScrollCell import v_EVENTS, FACTORIZING_KEYSYM
from config_interface.wdg.menus import PopUpMenu, FooterLine
from config_interface.wdg.cells import ScrollCell


class CnfScope:
    def __init__(self, cell):
        self.cell = cell

        self.cnfframeconfig = {'column': 0, 'row': 0}

        self.cnf_units = dict()

        self.eof = None

        self.scopes = {
            scope: True for scope in CRC.configs.scopes
        }

        self._switch_scope(self.scopes)

    def _switch_scope(self, update_: iter):
        if isinstance(update_, str): update_ = [update_]
        for scope in update_:
            self.scopes[scope] = self.scopes[scope] ^ True

        try:
            self.eof.forget()
        except AttributeError:
            pass

        with open(configuration_sheet.__file__) as f:
            for i in range(CRC.configs.cnf_max_lines + 1):

                ln = f.readline().strip()
                if not ln or ln.startswith('#'): continue
                if search("\$eof\$", ln): break
                if not (cnfln := search(CRC.configs.cnf_ln_re, ln)): continue

                cnfln = cnfln.group()
                attr = search(value_name_re, ln).group()
                cnfunit = search(CRC.configs.cnf_units_re, cnfln).group()

                is_uni_scope = True
                for scope in self.scopes:
                    if search(CRC.configs.scopes_re[scope], cnfln):
                        is_uni_scope = False
                        if scope in update_:
                            if self.scopes[scope] and (not self.cnf_units.get(cnfunit) or not self.cnf_units[cnfunit].get(attr)):
                                self._setrow(cnfunit, attr, ln)
                            elif not self.scopes[scope]:
                                self._usetrow(cnfunit, attr)
                if is_uni_scope:
                    if not hasattr(self, "row_" + attr):
                        self._setrow(cnfunit, attr, ln)
            assert i != CRC.configs.cnf_max_lines, f"{CRC.configs.cnf_max_lines=}; missing `$eof$`"
        self.eof = EOF(self.cell)

    def _usetrow(self, cnfunit, attr):
        try:
            getattr(self, "row_" + attr).pack_forget()
            self.cnf_units[cnfunit].pop(attr)
            if not self.cnf_units[cnfunit]:
                getattr(self, 'unit_' + cnfunit).grid_forget()
                self.cnf_units.pop(cnfunit)
        except AttributeError:
            pass

    def _setrow(self, cnfunit, attr, ln):

        if cnfunit not in self.cnf_units:
            unit = SectorFrame(self.cell, cnfunit)
            unit.grid(**self.cnfframeconfig, sticky=EW)
            texts.txtCell.add_wiki_attr(unit.label, cnfunit)
            setattr(self, 'unit_' + cnfunit, unit)
            self.cell.scroll_update(unit)
            self.cell.scroll_update(unit.label)
            self.cnf_units[cnfunit] = dict()
            self.cnfframeconfig['row'] += 1

        row = CnfRow(
            master := getattr(self, 'unit_' + cnfunit),
            attr,
            ln
        )
        row.pack(anchor=W, fill=X)
        texts.txtCell.add_wiki_attr(row.label, attr)

        widget_close.bind(row)

        InfoPopUp(row.label, get_infopop_lines(attr), font=CRC.fonts['main'].attrpop_font)

        if MOD_DEBUG:
            _popup_methods = (
                ("None", "Fill", "Default", None, "Print"),
                (lambda: row.cnf.setnone(),
                 lambda: row.cnf.fill(getattr(default_values, value_name2default_name(attr))),
                 lambda: row.cnf.setval(getattr(default_values, value_name2default_name(attr))),
                 None,
                 lambda: print(row.cnf.cnf))
            )
        else:
            _popup_methods = (
                ("None", "Fill", "Default"),
                (lambda: row.cnf.setnone(),
                 lambda: row.cnf.fill(getattr(default_values, value_name2default_name(attr))),
                 lambda: row.cnf.setval(getattr(default_values, value_name2default_name(attr))))
            )

        PopUpMenu(
            master,
            *_popup_methods,
            (row.label,)
        )

        self.cnf_units[cnfunit][
            attr
        ] = row
        
        self.cell.FACTORIZING_KEYSYM = list(FACTORIZING_KEYSYM)
        self.cell.FACTORIZING_KEYSYM.remove("Down")
        self.cell.FACTORIZING_KEYSYM.remove("Up")
        self.cell.FACTORIZING_KEYSYM = tuple(self.cell.FACTORIZING_KEYSYM)
        self.cell.v_EVENTS = list(v_EVENTS)
        self.cell.v_EVENTS.extend(["<Up>", "<Down>"])
        self.cell.v_EVENTS = tuple(self.cell.v_EVENTS)

        self.cell.scroll_update(row)
        self.cell.scroll_update(row.label)
        
        for w in row.cnf.all_wg:
            self.cell.scroll_update(w, "V")

        setattr(self, "row_" + attr, row)


class CnfMainTab(CnfScope):

    def __init__(self, ROOT_TK):

        self.root = ROOT_TK

        self.CellLeft = ScrollCell(master=TAB_CTL.MAIN_TAB)
        self.CellLeft.grid(row=0, column=0)

        self.CellRight = ScrollCell(master=TAB_CTL.MAIN_TAB)
        self.CellRight.grid(row=0, column=1)

        self.txtCell = texts.TextCell(self.CellRight)

        widget_close.bind(self.txtCell.text)
        widget_close.bind(self.CellRight.scrollbar_y)
        widget_close.bind(self.CellLeft.scrollbar_y)

        if MOD_DEBUG:
            PopUpMenu(
                ROOT_TK,
                ("Insert previous page", "Flush", None, "State to r+", "Disable clear automatic"),
                (self.txtCell.clipboard_insert, self.txtCell.flush, None,
                 lambda: self.txtCell.state(),
                 lambda: self.txtCell.autoclear()),
                (self.txtCell.text,),
                i_is_check=(3, 4)
            )
        else:
            PopUpMenu(
                ROOT_TK,
                ("Insert previous page", "Flush", None, "Disable clear automatic"),
                (self.txtCell.clipboard_insert, self.txtCell.flush, None,
                 lambda: self.txtCell.autoclear()),
                (self.txtCell.text,),
                i_is_check=(3,)
            )

        self.CellRight.scroll_update(self.txtCell.text)

        CnfScope.__init__(self, self.CellLeft)

        self.footerFrameL = FooterLine.Left(
            TAB_CTL.MAIN_TAB, 1, 0
        )

        self.footerFrameR = FooterLine.Right(
            TAB_CTL.MAIN_TAB, 1, 1
        )

        widget_close.bind(self.footerFrameL)
        widget_close.bind(self.footerFrameR)

        self.footerFrameR.update_text("theme", "--------------")
        self.footerFrameL.update_text(self.scopes)

    def filldefaults(self):
        for name, val in default_values.__dict__.items():
            if hasattr(self, (_attr := "row_" + default_name2value_name(name))):
                getattr(self, _attr).cnf.fill(val)
        TAB_CTL.update_tabs_()

    def setnone(self):
        for unit in self.cnf_units:
            for row in self.cnf_units[unit]:
                self.cnf_units[unit][row].cnf.setnone()
        TAB_CTL.update_tabs_()

    def setdefaults(self):
        for name, val in default_values.__dict__.items():
            if hasattr(self, (_attr := "row_" + default_name2value_name(name))):
                getattr(self, _attr).cnf.setval(val)
        TAB_CTL.update_tabs_()

    def consume(self):
        self.txtCell.delete()
        for unit in self.cnf_units:
            for row in self.cnf_units[unit]:
                self.cnf_units[unit][row].cnf.get()
        TAB_CTL.update_tabs_()

    def fillfile(self):
        self._sourcefile()
        TAB_CTL.update_tabs_()

    def sourcefile(self):
        self._sourcefile(True)
        TAB_CTL.update_tabs_()

    def _sourcefile(self, strict=False):
        if not (_file := askopenfilename()):
            return
        _ifdefs = list()
        _endifs = list()
        _defifendif = list()
        for board in IFDEFENDIF:
            if DefIfEndIf(_file,
                              *CRC.configuration_sheet.IFDEFENDIF[board]).configured:
                _ifdefs.append(CRC.configuration_sheet.IFDEFENDIF[board][0].replace(b' ', b'').decode(ENCODING))
                _endifs.append(CRC.configuration_sheet.IFDEFENDIF[board][1].replace(b' ', b'').decode(ENCODING))
                _defifendif.append(board)
        with open(_file) as f:
            n_lines = range(f.read().count('\n') + 1)
        with open(_file) as f:
            for _ in n_lines:
                ln = f.readline().strip()
                if ln.replace(' ', '') in _ifdefs:
                    _ifdefs.remove(ln.replace(' ', ''))
                    while True:
                        ln = f.readline().strip()
                        if ln.replace(' ', '') in _endifs:
                            _endifs.remove(ln.replace(' ', ''))
                            break
                if ln.startswith('#'): continue
                if not ln: continue
                _attr = search("^\w+", ln)
                if _attr:
                    _attr = _attr.group()
                    if not hasattr(CRC.configuration_sheet, _attr):
                        raise AttributeError(f"NoConfigurationAttribute : '{_attr}'")
                    _val = sub(_attr + "\s*:?[^=]*=\s*", "", ln)
                    try:
                        _val = literal_eval(_val)
                    except SyntaxError as e:
                        self.txtCell.insert(_attr, CRC.strings.errmsg_corresponding_val % e.text)
                        _val = None
                    except ValueError as e:
                        self.txtCell.insert(_attr, CRC.strings.errmsg_corrupted_val)
                        _val = None
                    if hasattr(self, (_row := "row_" + _attr)):
                        if strict:
                            getattr(self, _row).cnf.setval(_val)
                        else:
                            getattr(self, _row).cnf.fill(_val)
        for board in _defifendif:
            if hasattr(self, (_row := "row_" + board)):
                getattr(self, _row).cnf.setval(_file)

    def savefile(self):
        if not (file := asksaveasfilename()):
            return
        self.txtCell.delete()
        with open(file, "w") as f:
            for unit in self.cnf_units:
                min_count = 0
                for _min in CRC.configs.cnf_units_mins[unit]:
                    if self.cnf_units[unit][_min].cnf.get() is not None:
                        min_count += 1

                unit_msg = f"\n\n# [ {unit} ]\n"
                if len(CRC.configs.cnf_units_mins[unit]) > min_count > 0:
                    self.txtCell.insert(unit_msg,
                                        CRC.strings.errmsg_min_cnf % (unit, str(CRC.configs.cnf_units_mins[unit])))
                    continue

                self.txtCell.unit_append(_str=unit_msg + '\n')
                f.write(unit_msg + '\n')

                for row in self.cnf_units[unit]:
                    _val = self.cnf_units[unit][row].cnf.get()
                    if isinstance(_val, str):
                        f.write(f"{row}={_val!r}\n")
                    else:
                        f.write(f"{row}={_val}\n")
                    self.txtCell.unit_append(row, CRC.strings.errmsg_write % str(_val))
                self.txtCell.unit_flush()

    def choosecolor(self, setmeth):
        for unit in self.cnf_units:
            for row in self.cnf_units[unit]:
                self.cnf_units[unit][row].cnf.choosecolor(setmeth)
                CRC.colors.color_state([self.cnf_units[unit][row]],
                                       ['color_main_bg'],
                                       ['color_main_fg'],
                                       setmeth)

        self.txtCell.choosecolor(setmeth)
        self.CellRight.choosecolor(setmeth)
        if CRC.colors.rm_choose_state:
            PopUpMenu(
                ROOT_TK,
                ("Insert previous page", "Flush", None, "State to r+", "Disable clear automatic"),
                (self.txtCell.clipboard_insert, self.txtCell.flush, None,
                 lambda: self.txtCell.state(),
                 lambda: self.txtCell.autoclear()),
                (self.txtCell.text,),
                i_is_check=(3, 4)
            )
            widget_close.bind(self.CellRight.scrollbar_y)
