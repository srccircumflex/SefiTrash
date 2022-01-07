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

from tkinter import Label, Text, Button
from tkinter import W, END, E, NSEW

from config_interface._rc import _run as CRC
from config_interface.wdg.InfoPopUp import InfoPopUp
from config_interface.wdg.plugin_widgets import ScrollCell, TextCell
from config_interface.tab_plugins.SSLPEM import configKey, msg_strings, openssl
from config_interface.tab_plugins.SSLPEM.openssl_cnf import OpenSSLCnfText
from config_interface.tab_plugins.SSLPEM.openssl_args import OpenSSLArgs
from config_interface.tab_plugins.SSLPEM.openssl_run import RunOpenSSL


class LogText:

    def __init__(self, master):
        self.text = Text(master,
                         height=int(CRC.geo.main_height * 0.2),
                         width=(CRC.geo.main_width * 2) // CRC.fonts.width_divisor,
                         font=CRC.fonts.main_font,
                         )

    def top_insert(self, *args):
        self.text.insert("1.0", str().join(args))

    def insert(self, *args):
        self.text.insert(END, str().join(args))

    def delete(self):
        self.text.delete("1.0", END)


class _Cells:
    def __init__(self, _self):
        self.cell_l = ScrollCell(_self.tabFrame,
                                 configKey,
                                 cell_kwargs={'height': int(CRC.geo.main_height * 0.8),
                                              'width': CRC.geo.main_width},
                                 scrollbar_kwargs={'width': CRC.geo.scrollbar_width}
                                 )

        self.cell_b = ScrollCell(_self.tabFrame,
                                 configKey,
                                 cell_kwargs={'height': int(CRC.geo.main_height * 0.2),
                                              'width': CRC.geo.main_width * 2},
                                 scrollbar_kwargs={'width': CRC.geo.scrollbar_width}
                                 )

        self.cmd_container = Label(_self.tabFrame)
        self.cmd_container.grid(row=0, column=1, sticky=NSEW)

        self.log_text = LogText(self.cell_b)
        self.log_text.text.grid()
        self.log_text.insert(msg_strings.DESCRIPTION_B)

        self.err_text = TextCell(self.cmd_container, configKey,  sticky=NSEW, pady=35, row=10, columnspan=2)
        self.err_text.insert(_str=msg_strings.DESCRIPTION)

        self.openssl_cnf_text = OpenSSLCnfText(self.cell_l, self.err_text)

        self.cell_l.scroll_update(self.openssl_cnf_text)
        self.cell_b.scroll_update(self.log_text.text)
        self.cell_l.grid(row=0, column=0, sticky=W)
        self.cell_b.grid(row=1, column=0, columnspan=2)
        self.openssl_cnf_text.grid()


class OpenSSL(_Cells):
    def __init__(self, _root_cls):

        _Cells.__init__(self, _root_cls)

        self.openssl_args = OpenSSLArgs(self.cmd_container, self.log_text, _root_cls.Groot.MAIN_TAB.cnf_units)

        self.run = Button(self.cmd_container,
                          text=" run ",
                          command=self.run_openssl,
                          font=CRC.fonts.main_font,
                          image=CRC.fonts[configKey].ico_openssl,
                          relief="flat",
                          bd=0)
        self.run.grid(row=6, column=1, sticky=E)

        InfoPopUp(self.run,
                  ["run openssl"],
                  foreground=CRC.colors[configKey].color_infopop_fg,
                  background=CRC.colors[configKey].color_infopop_bg,
                  font=CRC.fonts[configKey].infopop_font
                  )

    def run_openssl(self):
        self.openssl_args.savePW()
        cmds = [""]
        cmds[0] += self.openssl_args.prog.get() + ' '
        cmds[0] += self.openssl_args.firsts.get() + ' '
        if not (keyout := self.openssl_args.keyout.get()):
            return self.err_text.insert(_str=msg_strings.ERR % f"{keyout=}")
        cmds[0] += openssl.KEY_OUT % keyout
        if not (certout := self.openssl_args.certout.get()):
            return self.err_text.insert(_str=msg_strings.ERR % f"{certout=}\n")
        cmds[0] += openssl.CRT_OUT % certout
        cmds[0] += self.openssl_args.passout.getarg() + ' '
        cmds[0] += self.openssl_args.lasts.get()

        cmds.append("")
        if 'x509' in cmds[0]:
            cmds[1] = self.openssl_args.prog.get() + ' ' + openssl.LOOKUP % certout

        if not self.openssl_cnf_text.manp_configfile():
            return self.err_text.insert(_str=msg_strings.ERR % f"in file {openssl.OPENSSL_CNF}")

        self.openssl_cnf_text.write()

        RunOpenSSL(cmds, self.log_text)
