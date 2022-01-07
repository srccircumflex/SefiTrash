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

from tkinter import Text
from tkinter import END

from re import sub, compile, search

from config_interface._rc import _run as CRC
from config_interface.wdg.tools import TextHighlighting
from config_interface.tab_plugins.SSLPEM import openssl, msg_strings


class OpenSSLCnfText(Text):

    def __init__(self, master, err_text):
        Text.__init__(self, master,
                      height=int(CRC.geo.main_height * 0.8),
                      width=CRC.geo.main_width // CRC.fonts.width_divisor,
                      font=CRC.fonts.main_font,
                      insertbackground="#C4A000"
                      )

        self.err_text = err_text

        with open(openssl.OPENSSL_CNF) as f:
            self.insert("1.0", f.read())

        for event in ("<KeyRelease-Up>", "<KeyRelease-Down>", "<KeyRelease-Left>", "<KeyRelease-Right>",
                      "<KeyRelease-Return>", "<KeyRelease-space>", "<BackSpace>", "<Delete>"):
            self.bind(event, lambda _: self.after(100, self.manp_configfile))

        for event in ("<Leave>", "<Control-Tab>", CRC.SHIFT_TAB):
            self.bind(event, lambda _: self.after(100, self.manp_configfile, True))

        self.bind("<Alt-R>", self._reset)

        self.subj_section = None
        self.subj_section_in = False
        self.prompt_no = False
        self.req_section_i = None

        self.th = TextHighlighting(
            self,
            main_config={
                compile("^\[ req ]"): {'background': '#E2E645', 'font': CRC.fonts.main_font_bold},
                compile("^prompt\s*=\s*no"): {'background': '#E2E645', 'font': CRC.fonts.main_font_underl},
                compile("^distinguished_name"): {'background': '#4591E6'},
            },
            at_call={
                compile("^\[ req ]"): lambda ln, n, m: setattr(self, 'req_section_i', "%d.%d" % (n, m.end())),
                compile("^prompt\s*=\s*no"): lambda *_: setattr(self, 'prompt_no', True)
            }
        )

        def _subj_section(ln, *_):
            subj_section = sub("^distinguished_name|\s|=|#.*", "", ln)
            self.th.sub_loop = [
                {compile(f"^\[ {subj_section} ]"): {'background': '#4591E6', 'font': CRC.fonts.main_font_bold}},
                {compile("^\[")},
                {
                    compile("^[^#].+"): {'background': '#5CA3F2'},
                    compile("(?<=#).*"): {'background': '#555E68', 'foreground': 'white'},
                    compile("^#+"): {'background': 'red', 'foreground': 'black'},
                }
            ]
            self.th.at_call |= {
                compile(f"^\[ {subj_section} ]"): lambda *_: setattr(self, 'subj_section_in', True)
            }

        self.th.at_call |= {compile("^distinguished_name"): _subj_section}

        self.manp_configfile()

    def manp_configfile(self, imports=False) -> bool:
        if imports:
            importlns = []
            importidx = []
            for n, ln in enumerate(self.get("1.0", END).splitlines(True), 1):
                if m := search("^\.include.*\n", ln):
                    importlns.append(m.group())
                    importidx.append(("%d.0" % n, "%d.%d" % (n, m.end() + 1)))

            for i in importidx:
                self.delete(*i)

            cont = self.get("1.0", END)
            self.delete("1.0", END)
            self.insert("1.0", str().join(importlns) + cont.strip())

        _r = True

        self.subj_section = None
        self.subj_section_in = False
        self.prompt_no = False
        self.req_section_i = None

        self.th.highlight(True)

        if not self.req_section_i:
            self.err_text.insert(_str=msg_strings.ERR % "section '[ req ]' missing")
            _r = False

        elif not self.prompt_no:
            self.insert(self.req_section_i, "\n\nprompt = no")
            self.th.highlight(True)

        return _r

    def write(self):
        with open(openssl.OPENSSL_CNF, "w") as f:
            f.write(self.get("1.0", END))

    def _reset(self, *_):
        self.delete("1.0", END)
        with open(openssl.OPENSSL_CNF_B) as f:
            self.insert("1.0", f.read())
        self.manp_configfile(True)
