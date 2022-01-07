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

from re import search
from config_interface._rc.base_cls import AddRCChild

_root_folder = search(".*[/\\\]", __file__).group()

additional_config_file = "config.conf"
additional_color_table = "color.conf"

additional_config_file = _root_folder + additional_config_file
additional_color_table = _root_folder + additional_color_table

configKey = search("(?<=[/\\\])\w+(?=[/\\\]configs\.py$)", __file__).group()


class RCColor(AddRCChild):

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.color_theme = self._root.main.color_theme
        self.source_config(additional_color_table)


class RCConfig(AddRCChild):

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.source_config(additional_config_file)


class RCGeo(AddRCChild):

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.source_config(additional_config_file)

class RCGeo2(AddRCChild):

    key = "SSLPEM2"

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.source_config(additional_config_file)
        self.entry_str = 100

class RCFont(AddRCChild):

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.source_config(additional_config_file)


class RCString(AddRCChild):

    def __init__(self, _root_cls):
        AddRCChild.__init__(self, _root_cls)
        self.source_config(additional_config_file)
