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

from tkinter import PhotoImage

from os import scandir
from re import search, sub, compile
from ast import literal_eval

from config_interface import ROOT_DIR

ICO_SOURCE = ROOT_DIR + "/_rc/ico/%(png)s"
PLUGIN_SOURCE = ROOT_DIR + "/tab_plugins"
ADD_CONF_IMPORT_STR = "config_interface.tab_plugins.%(add_root)s.configs"

def __tag_kwargs(self, line):
    _attr = search("(?<=gui_)tag_[^_]+(?=_)", line).group()
    _val = sub("\w+\s*\|\s*|\s*#.*", "", line.strip())
    _key = search("(?<=_)[a-z]+(?=\s)", line).group()
    try:
        _cls_attr = getattr(self, _attr)
    except KeyError:
        setattr(self, _attr, {})
        _cls_attr = getattr(self, _attr)
    if _val in ('', '0', 'none', 'None', '-'):
        getattr(self, _attr).setdefault(_key, None)
    else:
        getattr(self, _attr).setdefault(_key, '#' + _val)


__add_rc_id_source__ = {
    "RCGeo": {compile("^geo_"): {
        compile("^geo_float_"): lambda self, ln: setattr(self, search("(?<=float_)\w+", ln).group(),
                                                         float(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))),
        compile("^geo_int_"): lambda self, ln: setattr(self, search("(?<=int_)\w+", ln).group(),
                                                       int(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip())))
    }},
    "RCFont": {compile("^fnt_"): {
        compile("^fnt_int_"): lambda self, ln: setattr(self, search("(?<=fnt_int)\w+", ln).group(),
                                                       int(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))),
        compile("^fnt_ico_"): lambda self, ln: setattr(self, search("(?<=fnt_)ico_\w+", ln).group(),
                                                       PhotoImage(file=ICO_SOURCE % {
                                                           'png': sub("\w+\s*\|\s*|\s*#.*", "", ln.strip())
                                                       })),
        compile("^fnt_scale_"): lambda self, ln: setattr(
            self, _attr := "ico_" + search("(?<=fnt_scale_)\w+", ln).group(),
            getattr(
                self,
                _attr
            ).subsample(
                *literal_eval(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))
            )
        )
    }},
    "RCColor": {compile("^color_"): {
        compile("^color_theme_auto_source"): lambda self, ln: print(f"[i] {self!r}"),
        compile("^color_theme"): lambda self, ln: print(f"[i] {self!r}"),
        compile("^color_zebra"): lambda self, ln: print(f"[i] {self!r}"),
        compile("^color_"): lambda self, ln: setattr(self, search("\w+", ln).group(),
                                                     '#' + sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))
    }},
    "RCString": {compile("^label_|^errmsg_"): {
        compile("^label_|^errmsg_"): lambda self, ln: setattr(self, search("\w+", ln).group(),
                                                              sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))
    }},
    "RCConfig": {compile("^gui_"): {
        compile("^gui_color_"): lambda self, ln: setattr(self, search("(?<=gui_color_)\w+", ln).group(),
                                                         '#' + sub("\w+\s*\|\s*|\s*#.*", "", ln.strip())),
        compile("^gui_str_"): lambda self, ln: setattr(self, search("(?<=gui_str_)\w+", ln).group(),
                                                       sub("\w+\s*\|\s*|\s*#.*", "", ln.strip())),
        compile("^gui_int_"): lambda self, ln: setattr(self, search("(?<=gui_int_)\w+", ln).group(),
                                                       int(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))),
        compile("^gui_float_"): lambda self, ln: setattr(self, search("(?<=gui_float_)\w+", ln).group(),
                                                         float(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))),
        compile("^gui_list_"): lambda self, ln: setattr(self, search("(?<=gui_list_)\w+", ln).group(),
                                                        literal_eval(sub("\w+\s*\|\s*|\s*#.*", "", ln.strip()))),
        compile("^gui_tag_"): __tag_kwargs
    }}
}


class AddRCMain:
    additional_tab_roots = [e.name for e in list(scandir(PLUGIN_SOURCE))
                            if e.is_dir() and not e.name.startswith('_')]

    __add_rc_ids__ = tuple(__add_rc_id_source__)  # ["RCGeo", "RCFont", "RCColor", "RCString", "RCConfig"]

    def __init__(self):
        """
        - config_id: ["RCGeo", "RCFont", "RCColor", "RCString", "RCConfig"] initialed by child class
        
        for add_root in /sec/add:
            import add_root.configs
            for add_config in add_root.configs:
                if add_config.startswith(config_id):
                    add_config.setdefault(key, add_root)
                    setattr(self, add_config.key, add_config())
        """

        for add_root in self.additional_tab_roots:
            module = __import__(ADD_CONF_IMPORT_STR % {'add_root': add_root}, globals(), locals(), [""], 0)
            for add_attr in module.__dict__:
                if add_attr.startswith(self._config_id):
                    if not hasattr(_cls := module.__dict__[add_attr], "key"):
                        setattr(_cls, "key", add_root)
                    setattr(self, _cls.key, _cls.__call__(self))

    def __getitem__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            return self.main

    def __getattr__(self, item):
        try:
            return self.__dict__['main'].__dict__[item]
        except KeyError:
            return self.__dict__[item]


class AddRCChild:
    """
    config_id: ["RCGeo", "RCFont", "RCColor", "RCString", "RCConfig"]
    key: default = packet name

    class RCGeoMain:
    ....def __init__(self):
    ........self.main = self.Main(self)
    ........setattr(self, AddRCChild.key, AddRCChild(self))
    ....class Main:
    ........  ...
    """

    def __init__(self, _root_cls):
        """
        config_id: ["RCGeo", "RCFont", "RCColor", "RCString", "RCConfig"]
        key: default = packet name

        class RCGeoMain:
        ....def __init__(self):
        ........self.main = self.Main(self)
        ........setattr(self, AddRCChild.key, AddRCChild(self))
        ....class Main:
        ........  ...

        :param _root_cls: (by main class)  
        """

        self._root = _root_cls
        self._config_id_re = list(__add_rc_id_source__[self._root._config_id])[0]
        self._config_types = __add_rc_id_source__[self._root._config_id][self._config_id_re]

    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            return getattr(self._root, item)

    def source_config(self, file):
        try:
            with open(file) as f:
                for _ in range(300):
                    ln = f.readline()
                    if not ln or ln.startswith('#'): continue
                    if not search(self._config_id_re, ln): continue
                    for _type_re in self._config_types:
                        if search(_type_re, ln):
                            self._config_types[_type_re].__call__(self, ln)
        except FileNotFoundError as e:
            print(f"{self} {e}")
