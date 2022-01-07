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

from tkinter import Label, Checkbutton, IntVar
from tkinter import W, DISABLED, NORMAL

from config_interface.prc import configtypeobjs as COJ
from config_interface._rc import _run as CRC
from config_interface.tab_plugins.SSLPEM import configKey, TARGET_UNIT, openssl


class PassOut(COJ.type_pass):

    def __init__(self, container, save_checkbutton: Checkbutton, cnf_units: dict, **grid_kwargs):

        self.save_checkbutton = save_checkbutton
        self.cnf_units = cnf_units

        _container = Label(container)

        self.check_v = IntVar()
        self.check = Checkbutton(_container,
                                 text=openssl.NODES,
                                 variable=self.check_v,
                                 command=self.passnopass,
                                 font=CRC.fonts.main_font_bold)
        self.check.grid(row=0, column=0)

        COJ.type_pass.__init__(self,
                               _container,
                               "",
                               " 0$pass;{sha256}$",
                               configKey,
                               None,
                               row=0, column=2)
        self.entry.config(state=DISABLED)

        _container.grid(grid_kwargs)

    def passnopass(self):
        if self.check_v.get():
            self.check.config(text=openssl.PASS_OUT.replace('%s', ''))
            self.entry.config(state=NORMAL)
            self.save_checkbutton.config(state=NORMAL)
        else:
            self.check.config(text=openssl.NODES)
            self.entry.config(state=DISABLED)
            self.save_checkbutton.config(state=DISABLED)

    def getarg(self):
        if self.check_v.get():
            print(self.get())
            return openssl.PASS_OUT % self.get()
        return openssl.NODES

    def saveSSL_PASSWORD(self, save_pw_v: int):
        if save_pw_v and self.check_v.get():
            self.cnf_units[TARGET_UNIT]['SSL_PASSWORD'].cnf.setval(self.entry.get())


class OpenSSLArgs:

    def __init__(self, cmd_container, log_text, cnf_units):

        self.log_text = log_text

        self.prog = COJ.type_str(cmd_container,
                                 "",
                                 "",
                                 configKey,
                                 None,
                                 row=0,
                                 column=0,
                                 sticky=W,
                                 pady=10)
        Label(cmd_container, text="{").grid(row=0, column=1)

        self.firsts = COJ.type_str(cmd_container,
                                   "",
                                   "",
                                   configKey,
                                   None,
                                   row=1,
                                   column=0,
                                   sticky=W,
                                   pady=3)

        self.keyout = COJ.type_wfile(cmd_container,
                                     "",
                                     " 0$wfile;{6}$",
                                     configKey,
                                     log_text,
                                     row=2,
                                     column=0,
                                     sticky=W,
                                     pady=3)
        Label(self.keyout.button_kw['master'], font=self.keyout.button_kw['font'],
              text=openssl.KEY_OUT % "`SSL_KEY_FILE' ").grid(row=0, column=1)

        self.certout = COJ.type_wfile(cmd_container,
                                      "",
                                      " 0$wfile;{6}$",
                                      configKey,
                                      log_text,
                                      row=3,
                                      column=0,
                                      sticky=W,
                                      pady=3)
        Label(self.certout.button_kw['master'], font=self.keyout.button_kw['font'],
              text=openssl.CRT_OUT % "`SSL_CERT_FILE'").grid(row=0, column=1)

        self.lasts = COJ.type_str(cmd_container,
                                  "",
                                  "",
                                  configKey,
                                  None,
                                  row=5,
                                  column=0,
                                  sticky=W,
                                  pady=3)

        Label(cmd_container, text="}").grid(row=6, column=0, sticky=W, pady=10)

        self.prog.setval(openssl.OPENSSL_CMD)
        self.firsts.setval(openssl.FIRST_LN)
        self.lasts.setval(openssl.END_LN)

        self.save_passw_v = IntVar()
        self.save_passw = Checkbutton(cmd_container,
                                      text="save `SSL_PASSWORD'",
                                      font=CRC.fonts.main_font,
                                      variable=self.save_passw_v,
                                      state=DISABLED,
                                      command=self.savePW)
        self.save_passw.grid(row=6, column=0)

        self.passout = PassOut(cmd_container,
                               self.save_passw,
                               cnf_units,
                               row=4,
                               column=0,
                               sticky=W,
                               pady=3)

    def savePW(self):
        self.passout.saveSSL_PASSWORD(self.save_passw_v.get())
