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
from gzip import open as gzipopen

from config_interface import MOD_DEBUG
from config_interface._rc import _run as CRC


def get_all_keys(_file) -> list:
    _set = list()
    flncount = 0
    with gzipopen(_file, "rt") as f:
        while not search("\$\$\$%\(EOF\)", ln := f.readline()):
            flncount += 1
            if m := search("(?<=\$\$\$%\()!?\w+(?=\)\n)", ln):
                _set.append(m.group())
            if flncount > 20000:
                raise EOFError(f"--ERROR: line limit = 20000 : $$$%(EOF) not matched : breaking loop--")
    return _set


def gen_infolines(_key, _file=CRC.attr_info_rev_file, debug=True):
    plncount = 0
    flncount = 0
    with gzipopen(_file, "rt") as f:
        while not plncount:
            ln = f.readline()
            if search(f"^\$\$\$%\({_key}\)$", ln):
                while True:
                    ln = f.readline()
                    plncount += 1
                    if search("^\$\$\$%\(!?\w+\)$", ln):
                        return
                    elif plncount > 300:
                        yield "\n" \
                              "----------------------------------------------------\n" \
                              "--ERROR: line limit per page = 300 : breaking loop--\n" \
                              "----------------------------------------------------\n"
                        raise EOFError(f"--ERROR: line limit per page = 300 : breaking loop--\n{_key=}")

                    if not debug and ln.startswith(' '):
                        continue

                    yield ln

            flncount += 1
            if flncount > 20000:
                yield "\n" \
                      "------------------------------------------------------------\n" \
                      "--ERROR: line limit = 20000 : noting found : breaking loop--\n" \
                      "------------------------------------------------------------\n"
                raise EOFError(f"--ERROR: line limit = 20000 : noting found : breaking loop--\n{_key=}")


def get_infopop_lines(_key) -> list:
    lines = list()
    _g = gen_infolines(_key, _file=CRC.attr_info_pop_file, debug=MOD_DEBUG)
    while True:
        try:

            ln = next(_g).strip()
            if ln in ('---', ' ---'):
                lines.append(None)
            else:
                lines.append(ln)

        except StopIteration:

            start = 0
            while not lines[start]:
                start += 1
            end = -1
            while not lines[end]:
                end -= 1

            if end == -1:
                end = None
            else:
                end = end + 1

            return lines[slice(start, end)]


def get_sheet_json(config_sheet, max_lines=500) -> dict[str, dict]:
    _json = dict()
    with open(config_sheet) as f:
        for i in range(max_lines + 1):

            ln = f.readline().strip()
            if not ln or ln.startswith('#'): continue
            if search("\$eof\$", ln): break
            if not (cnfln := search("\s\w+\$\d\d*\$\w", ln)): continue

            cnfln = cnfln.group()
            attr = search("^\w+", ln).group()
            cnfunit = search("(?<=\s)\w+(?=\$)", cnfln).group()

            if not _json.get(cnfunit):
                _json[cnfunit] = dict()
            _json[cnfunit][attr] = None

    return _json
