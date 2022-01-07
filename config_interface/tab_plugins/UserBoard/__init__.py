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

TARGET_UNIT = "Permissions"
TARGET_ATTR = "BOARD_USERS"
configKey = "UserBoard"
ROOT_DIR = __path__[0]

from config_interface.tab_plugins._base_cls import TabBase
from config_interface.tab_plugins.UserBoard import configs as CONFIG
from config_interface.tab_plugins.UserBoard.widgets import UserLineMethods


class Main(UserLineMethods, TabBase):

    def __init__(self, GUI_ROOT, tabFrame):
        TabBase.__init__(self, GUI_ROOT, tabFrame)
        UserLineMethods.__init__(self, self)
        globals()['INST'] = self

    def update(self):
        if val := self.Groot.MAIN_TAB.cnf_units[TARGET_UNIT][TARGET_ATTR].cnf.get():
            self.file_entry.setval(val)
            self.file_out.setval(val)
            self.fsc_out.setval(val)
