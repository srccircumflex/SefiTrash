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


class Basic:
    class SupportRare:
        italic = "3;"
        blink_rapid = "6;"
        hide = "8;"
        underline_doubly = "21;"
    reset = "0;"
    bold = "1;"
    dim = "2;"
    underline = "4;"
    blink = "5;"
    invert = "7;"
    strike = "9;"

reset = "0;"
bold = "1;"
dim = "2;"
underline = "4;"
blink = "5;"
invert = "7;"
strike = "9;"

class Font:
    class SupportRare:
        blackletter = "20;"
    default = "10;"
    XI = "11;"
    XII = "12;"
    XIII = "13;"
    XIV = "14;"
    XV = "15;"
    XVI = "16;"
    XVII = "17;"
    XVIII = "18;"
    XIX = "19;"

class Reset:
    all = "0;"
    normal_intensity = "22;"
    not_italic = "23;"
    not_blackletter = "23;"
    not_underlined = "24;"
    not_blink = "25;"
    not_invert = "27;"
    not_hide = "28;"
    not_strike = "29;"

class Special:
    class Ideogram:
        underline = "60;"
        underline_doubly = "61;"
        overline = "62;"
        overline_doubly = "63;"
        stress = "64;"
        reset = "65;"

    class SupportMintty:
        framed = "51;"
        encircled = "52;"
        not_framed = "54;"
        not_encircled = "54;"
        superscript = "73;"
        subscript = "74;"
        not_superscript = "75;"
        not_subscript = "75;"
    proportional_spacing = "26;"
    not_proportional_spacing = "50;"
    overlined = "53;"
    not_overlined = "55;"


def print_lookup(__esc: str = "\u001b"):
    for cat in (Basic, Font, Special):
        for attr, val in cat.__dict__.items():
            if attr.startswith('_'): continue
            if attr[0] in "SI":
                for _attr, _val in val.__dict__.items():
                    if _attr.startswith('_'): continue
                    end = "\n"
                    if _attr == "hide":
                        end = "(%s.%s.%s)\n" % (cat.__name__, attr, _attr)
                    print(__esc + '[' + _val[:-1] + 'm', "%s.%s.%s" % (cat.__name__, attr, _attr), __esc + '[m', end=end)
            else:
                print(__esc + '[' + val[:-1] + 'm', "%s.%s" % (cat.__name__, attr), __esc + '[m')
