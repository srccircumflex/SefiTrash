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

TARGET_UNIT = "Verification"
TARGET_ATTR = "SSL_CERT_FILE"
TARGET_LABEL = "OpenSSL"
configKey = "SSLPEM"
ROOT_DIR = __path__[0]

from sys import platform
from os import access, environ
from config_interface.tab_plugins.SSLPEM import msg_strings, openssl
from config_interface.tab_plugins.SSLPEM import openssl_run


if platform == "linux":
    for path in environ["PATH"].split(':'):
        if access(path + "/openssl", 1):
            openssl.OPENSSL_CMD = path + "/openssl"
            msg_strings.DESCRIPTION = msg_strings.LIN_DESCR
            msg_strings.DESCRIPTION_B = msg_strings.LIN_DESCR_B
            openssl_run.RunOpenSSL = openssl_run._RunOpenSSL
            break
    if not openssl.OPENSSL_CMD:
        openssl.OPENSSL_CMD = "/usr/bin/openssl"
        msg_strings.DESCRIPTION = msg_strings.NO_ACCESS
        msg_strings.DESCRIPTION_B = msg_strings.NO_ACCESS_B
else:
    if not openssl.OPENSSL_CMD:
        openssl.OPENSSL_CMD = "openssl"
        msg_strings.DESCRIPTION = msg_strings.WIN_DESCR
        msg_strings.DESCRIPTION_B = msg_strings.WIN_DESCR_B
    else:
        msg_strings.DESCRIPTION = msg_strings.WIN_DESCR
        msg_strings.DESCRIPTION_B = msg_strings.WIN_DESCR_B
        openssl_run.RunOpenSSL = openssl_run._RunOpenSSL


from config_interface.tab_plugins._base_cls import TabBase
from config_interface.tab_plugins.SSLPEM.widgets import OpenSSL
from config_interface.tab_plugins.SSLPEM.openssl_args import OpenSSLArgs

openssl.OPENSSL_CNF = ROOT_DIR + "/doc/openssl.cnf"
openssl.OPENSSL_CNF_B = ROOT_DIR + "/doc/~openssl.cnf"
openssl.END_LN = openssl.END_LN % openssl.OPENSSL_CNF

class Main(OpenSSL, TabBase):

    def __init__(self, GUI_ROOT, tabFrame):
        TabBase.__init__(self, GUI_ROOT, tabFrame)
        OpenSSL.__init__(self, self)
        globals()['INST'] = self

    def update(self):
        _entrys = {
            'SSL_KEY_FILE': self.openssl_args.keyout,
            'SSL_CERT_FILE': self.openssl_args.certout
        }
        for v, e in _entrys.items():
            if val := self.Groot.MAIN_TAB.cnf_units[TARGET_UNIT][v].cnf.get():
                e.setval(val)

