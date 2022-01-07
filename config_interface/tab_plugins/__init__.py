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


from os import scandir


PLUG_TABS_IMP_STR = [__package__ + '.' + e.name for e in list(scandir(__path__[0]))
                     if e.is_dir() and not e.name.startswith('_')]


def get_TABS():
    ADD_TABS = list()
    for add_root in PLUG_TABS_IMP_STR:
        package = __import__(add_root, globals(), locals(), [""], 0)
        if not hasattr(package, 'TARGET_LABEL'):
            setattr(package, 'TARGET_LABEL', add_root.split('.')[-1])
        globals()['TAB_' + package.TARGET_ATTR] = package
        ADD_TABS.append(package)
    return ADD_TABS

ADD_TABS = get_TABS()
