#! /usr/bin/python3.9
#
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


from sys import argv
from ast import literal_eval
from multiprocessing import Process, Manager
from sys import path as sys_path
from os import path

sys_path.insert(0, path.dirname(__file__))

if __name__ == '__main__':

    from _rc import configurations as CNF
    import _main
    hasattr(_main, "__file__")

    CNF.HOST_SIDE = True

    try:
        from _rc._run import configurations as CNF
        from _rc._SPAWNrc import main
        from sec.Loggers import LOGS_
    except Exception as e:
        print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
        CNF.EXP_EXIT(1)

    try:
        _kill_backup = {}
        while True:

            CNF._CNF_PROX = Manager().Namespace()

            cnf_tpickle = {}
            for _attr in CNF.__dir__():
                if _attr.startswith('_'): continue
                cnf_tpickle |= {_attr: getattr(CNF, _attr)}
            cnf_tpickle |= {'_CNF_PROX': CNF._CNF_PROX}

            prc = Process(target=main, args=(cnf_tpickle, _kill_backup))
            prc.start()
            prc.join()
            print(f"[[ {prc.exitcode} ]]")
            if prc.exitcode in CNF.SHUTDOWN_EXCO:
                LOGS_.blackbox.logg(61, CNF.STRINGS.SHUTDOWN, '-', prc.exitcode, ico=CNF.PRINT_ICOS.shutdown)
                CNF.EXP_EXIT(prc.exitcode)

            for _attr in CNF.__dir__():
                if _attr.startswith("_"): continue
                if _attr == "CNF_PROX": continue
                setattr(CNF, _attr,
                        getattr(CNF._CNF_PROX, _attr))

            def _delparing(_argv):

                CNF.PROVIDED_PARING = None
                _paring_kws = ('PROVIDED_PARING', 'PROVIDED_PARING_IP', 'PROVIDED_PARING_USER')
                _paring_settings = [_argv[_i] for _i in range(1, len(_argv), 2)
                                    if _argv[_i].upper() in _paring_kws]
                for _v in _paring_settings: _i = _argv.index(_v); _argv.pop(_i); _argv.pop(_i)

            _delparing(argv)

            with open(CNF.LOG_KILL, "r") as f:

                _ln = f.read().splitlines()[-2:-1][0].split(' # ')
                _delparing(_argv := literal_eval(_ln[-1]))

                for _i in range(1, len(_argv), 2):
                    if hasattr(CNF, _argv[_i].upper()):
                        print(f"SET: {_argv[_i].upper()} = {_argv[_i + 1]}")
                        setattr(CNF, _argv[_i].upper(), literal_eval(_argv[_i + 1]))

                if _lu := literal_eval(_ln[-2]):
                    for _ in _lu.copy():
                        if CNF.AUTH_CONF.get((_u := _lu.pop())):
                            CNF.AUTH_CONF.pop(_u)

                _kill_backup = literal_eval(_ln[-3])

    except KeyboardInterrupt:
        exit('')
    except Exception as e:
        print(f"|[ {type(e)} ]|[ {e} ]|[ {e.__traceback__.tb_frame}")
        CNF.EXP_EXIT(1)
