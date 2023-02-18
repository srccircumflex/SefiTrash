# MIT License
#
# Copyright (c) 2021 Adrian F. Höfflin
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

from __future__ import annotations
from typing import Callable
from re import search, sub, escape, compile, Pattern
from gzip import open as gz_open

from . import _exceptions
from .argletters import _ArgLetter
try:
    import consoleparser
except ImportError:
    from .. import consoleparser

class ConsoleParser:

    __doc__ = """
CONFIG = {
    'command': (
        function, 
        {
            n_opts | (from, to): {
                'short-opt-re': (_Mod, ...) | _Mod, 
                '--longopt': (_Mod, ...) | _Mod,
                ...,
            },
            None: "default opt (optional)"
        }
    ),
    ...,
}
    # n_opts        : int | iter
    # short opt re  : re.Pattern
    # --longopt     : string
    # _Mod          : (_String() | _Integer() | _Float() | _Boolean() | _LiteralEval()) [& OPTIONAL &| TO_EOL]
    """

    def __init__(self, __config: dict = None):
        """
        :param __config: *ConsoleParser.__doc__
        """
        self._debug: bool = False

        self.config: dict = (dict() if __config is None else __config)

        self.intercept_options: dict = {'--help': self.help}
        self._interception_key: str | False = False
        self._interception_opt: str | None = None
        self.look_up: dict | None = None
        self.cmd_look: str | None = None

        self.open_man = None
        if consoleparser.MANUAL_PAGES_FILE:
            self.open_man = lambda: open(consoleparser.MANUAL_PAGES_FILE, "r")
            if consoleparser.MANUAL_PAGES_GZIP:
                self.open_man = lambda: gz_open(consoleparser.MANUAL_PAGES_FILE, "rt")

        consoleparser._PRINTING = consoleparser._PRINTING()

        self.command: str | None = None
        self.cmd_line: str | None = None
        self.cmd_split: list | None = None

        self.selected_opts_args: dict | None = None
        self.parsed_opts_args: tuple[dict, dict] | None = None

        self.config_item: tuple | None = None
        self.default: [None, str] = None
        self.func = None

        self._conf_curcmd = None

    def splitter(self, cmd_line, _cut_fun: bool = True) -> list:
        self.cmd_split = []
        if _cut_fun:
            _cmd_line = sub("^\S+(\s+|$)", '', cmd_line)
        else:
            _cmd_line = cmd_line
        mask = False
        while _cmd_line:
            if m := search("^[^ ]*\\\\ ", _cmd_line):
                g = m.group()[:-2]
                if mask:
                    self.cmd_split[-1] += ' ' + g
                else:
                    self.cmd_split.append(g)
                mask = True
                _cmd_line = sub(m.re.pattern, '', _cmd_line, 1).strip()
            else:
                m = search("^[^ ]+", _cmd_line)
                g = m.group()
                if mask:
                    self.cmd_split[-1] += ' ' + g
                else:
                    self.cmd_split.append(g)
                mask = False
                _cmd_line = sub(m.re.pattern, '', _cmd_line, 1).strip()
        return self.cmd_split

    def _search_intercept(self, selected_opt: str):
        if selected_opt.startswith('--'):
            if selected_opt in self.intercept_options:
                self._interception_opt = self._interception_key = selected_opt
        else:
            for intercept_re in self.intercept_options:
                if not intercept_re.startswith('--') and search(f"^-{intercept_re}$", selected_opt):
                    self._interception_key = intercept_re
                    self._interception_opt = selected_opt
        return self._interception_key

    def _pars_opts_args(self, cmd_split: list) -> dict:
        self.selected_opts_args = {"": []}
        current_opt = ""
        for n, part in enumerate(cmd_split):
            if part.startswith('-'):
                self._search_intercept(part)
                self.selected_opts_args.setdefault(part, list())
                current_opt = part
            else:
                self.selected_opts_args[current_opt].append(part)
        return self.selected_opts_args

    def _get_verify_args(self, _key_config: [str, None], _key_selected: [str, None]) -> list:

        def mod2():
            if _key_selected:
                arg_re = compile(f"(?<=\s{_key_selected}\s).*")
            else:
                arg_re = compile(f"(?<={self.command}\s).*")
            cmd_line = self.cmd_line
            for consumed in arg_list:
                cmd_line = sub(sub(" ", "\\ ", escape(consumed)), "", cmd_line, 1)
            return search(arg_re, cmd_line).group().strip()

        z_args: _ArgLetter = self.config_item[1][_key_config]
        args = self.selected_opts_args[_key_selected]
        arg_list = []
        __key_selected = (_key_selected if _key_selected is not None else self.command)
        if not isinstance(z_args, tuple):
            z_args: tuple[_ArgLetter] = (z_args,)
        for n, mod in enumerate(z_args):
            if int(mod) == 0:
                if len(args) != 0:
                    raise _exceptions.ParsError(f"`{__key_selected}' takes no arguments")
            elif int(mod) == 1:
                try:
                    arg_list.append(mod(args[n]))
                except IndexError:
                    raise _exceptions.ParsError(f"{__key_selected} : {mod} missing at position {n + 1}")
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
            elif int(mod) == 2:
                try:
                    if not (arg := mod2()):
                        raise AttributeError
                    arg_list.append(mod(arg))
                except AttributeError:
                    raise _exceptions.ParsError(f"`{__key_selected}' takes {mod}")
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
            elif int(mod) == -1:
                try:
                    arg_list.append(mod(args[n]))
                except IndexError:
                    pass
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
            elif int(mod) == -2:
                try:
                    if arg := mod2():
                        arg_list.append(mod(arg))
                except (AttributeError, TypeError):
                    pass
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
            elif int(mod) == 3:
                try:
                    if not args[n:]:
                        raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} : missing first {mod}")
                    for n, arg in enumerate(args[n:], start=n):
                        arg_list.append(mod(arg))
                except _exceptions.ParsError as e:
                    raise e
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
            elif int(mod) == -3:
                try:
                    for n, arg in enumerate(args[n:], start=n):
                        arg_list.append(mod(arg))
                except Exception as e:
                    raise _exceptions.ParsError(f"{__key_selected} : position {n + 1} = {mod} : {e}")
        return arg_list

    def _get_verify_opts_args(self) -> tuple[dict, dict]:
        self.parsed_opts_args = ({'':[]},{'':[]})
        if isinstance(self.config_item[0], int):
            z_opts = range(self.config_item[0], self.config_item[0] + 1)
        else:
            z_opts = range(self.config_item[0][0], self.config_item[0][1] + 1)
        count = 0
        opt_keys = []
        default_args = {self.default: self.selected_opts_args.pop("")}

        for selected_opt in self.selected_opts_args:
            match = False
            for opt_conf in self.config_item[1]:
                if opt_conf is None:
                    continue
                if opt_conf.startswith('--') and selected_opt == opt_conf:
                    count += 1
                    match = True
                    break
                elif m := search(f"(?<=^-){opt_conf}$", selected_opt):
                    count += len(m.group())
                    match = True
                    break
            if not match:
                raise _exceptions.ParsError(f"unknown option : {selected_opt}")
            opt_keys.append(opt_conf)

        if not opt_keys and None in self.config_item[1]:
            self.selected_opts_args[None] = default_args[None]
            args = self._get_verify_args(None, None)
            self.parsed_opts_args = {None: args}, {None: args}
            return self.parsed_opts_args

        if (count > z_opts.stop - 1) or (count + (self.default is not None) < z_opts.start):
            raise _exceptions.ParsError(f"{self.command} : {z_opts.start} to {z_opts.stop - 1} options expected ({count=})")
        elif count not in z_opts:
            if self.default is not None:
                for opt_key in self.config_item[1]:
                    if opt_key.startswith('--'):
                        if opt_key == self.default:
                            default_key = opt_key
                            break
                    elif search(opt_key, self.default):
                        default_key = opt_key
                        break
                self.cmd_line = sub(f"^{self.command}", f"{self.command} {self.default} ", self.cmd_line)
                self.selected_opts_args = default_args
                try:
                    self._search_intercept(self.default)
                    args = self._get_verify_args(default_key, self.default)
                    if self.default.startswith('--'):
                        self.parsed_opts_args = {}, {self.default: args}
                        return self.parsed_opts_args
                    self.parsed_opts_args = {self.default: args}, {}
                    return self.parsed_opts_args
                except Exception as e:
                    if self._interception_key:
                        pass
                    else:
                        raise _exceptions.ParsError(e)

        for key, opt in zip(opt_keys, self.selected_opts_args):
            self.selected_opts_args[opt] = self._get_verify_args(key, opt)

        self.parsed_opts_args = ({
                   item[0]: item[1] for item in self.selected_opts_args.items()
                   if not item[0].startswith('--')
               }, {
                   item[0]: item[1] for item in self.selected_opts_args.items()
                   if item[0].startswith('--')
               })
        return self.parsed_opts_args

    def _heed_interception(self):
        def intercept():
            item = self.intercept_options[self._interception_key]
            if isinstance(item, tuple):
                raise _exceptions.Interception(item[0].__call__(**{item[1]: self}))
            raise _exceptions.Interception(item.__call__(self))

        if self._interception_key:
            self.selected_opts_args.pop(self._interception_opt)
            try:
                self._get_verify_opts_args()
            except Exception:
                pass
            return intercept()

        _options = self._get_verify_opts_args()
        if self._interception_key:
            return intercept()
        return _options

    def _cmd_line_from_list(self, *args: str):
        self.cmd_line = "".join([sub(" ", "\\ ", i) + " " for i in args]).strip()
        return self.cmd_line

    def _command_from_cmd_line(self):
        self.command = self.cmd_line.split()[0]
        if self.command not in self.config:
            cmd = self.command
            self.command = None
            raise _exceptions.UnknownCommandError(f"unknown command : {cmd}")

    def _func_by_command(self):
        self.func = self.config[self.command][0]

    def _config_item_by_command(self):
        self.config_item = list(self.config[self.command][1].items())[0]

    def _default_by_command(self):
        self.default = self.config[self.command][1].get(None)

    def _clear(self):
        self.command: str | None = None
        self.cmd_line: str | None = None
        self.cmd_split: list | None = None
        self.selected_opts_args: dict | None = None
        self.parsed_opts_args: tuple[dict, dict] | None = None
        self._interception_key: str | False = False
        self._interception_opt: str | None = None

    def _parser_basic(self, cmd_line: str):
        self.cmd_line = cmd_line.strip()
        self._command_from_cmd_line()
        self._func_by_command()
        self._config_item_by_command()
        self._default_by_command()
        self._interception_key = False

    def jpars_string(self, cmd_line: str) -> None | dict[list]:
        """
        :return: { "option": [args] } | None
        """
        self._clear()
        if not cmd_line:
            raise _exceptions.NoInputError
        self._parser_basic(cmd_line)
        self.splitter(self.cmd_line)
        return self._pars_opts_args(self.cmd_split)

    def jpars_list(self, __list: list) -> None | dict[list]:
        """
        :return: { "option": [args] } | None
        """
        return self.jpars_string(self._cmd_line_from_list(*__list))

    def jpars_argv(self, __argv: list) -> None | dict[list]:
        """
        :return: { "option": [args] } | None
        """
        return self.jpars_list(__argv[1:])

    def pars_and_verify_string(self, cmd_line: str, ignore_intercept: bool = False) -> None | tuple[dict, dict]:
        """
        :return:  ( { "-short option": [args] }, { "--long option": [args] } ) | None
        """
        if not self.jpars_string(cmd_line):
            return
        if ignore_intercept:
            return self._get_verify_opts_args()
        return self._heed_interception()

    def pars_and_verify_list(self, __list: list, ignore_intercept: bool = False) -> None | tuple[dict, dict]:
        """
        :return:  ( { "-short option": [args] }, { "--long option": [args] } ) | None
        """
        if not self.jpars_list(__list):
            return
        if ignore_intercept:
            return self._get_verify_opts_args()
        return self._heed_interception()

    def pars_and_verify_argv(self, __argv: list, ignore_intercept: bool = False) -> None | tuple[dict, dict]:
        """
        :return:  ( { "-short option": [args] }, { "--long option": [args] } ) | None
        """
        return self.pars_and_verify_list(__argv[1:], ignore_intercept)

    def get_parsed_and_verified(self) -> tuple[dict[list], dict[list]]:
        """
        :return: ( { "-short option": [args] }, { "--long option": [args] } )
        """
        return self.parsed_opts_args

    def get_parsed_selected(self) -> dict[list]:
        """
        :return: { "option": [args] }
        """
        return self.selected_opts_args

    def get_merged(self) -> None | tuple[tuple[str, list] | None, list] | False:
        """
        :return: ( ( "short options without '-' as oneliner", ["long options without '--'"] ) | None, [args] ) | None=nothing selected(valid)
        """
        short = ""
        longs = []
        args = []
        if not self.parsed_opts_args:
            return False
        if None in self.parsed_opts_args[0]:
            return None, self.parsed_opts_args[0][None]
        for short_item in self.parsed_opts_args[0].items():
            short += short_item[0][1:]
            args.extend(short_item[1])
        for longs_item in self.parsed_opts_args[1].items():
            if longopt := longs_item[0][2:]:
                longs.append(longopt)
            args.extend(longs_item[1])
        if short or longs or args:
            return (short, longs), args

    def get_by_option(self, __option: str | None, sorted_comparison: bool = True) -> None | list | bool:
        """
        :return: [args] | True
        """
        def _sort_str(__s: str):
            __s = list(__s)
            __s.sort()
            return str().join(__s)
        if not self.parsed_opts_args:
            return
        if __option is None or __option.startswith('--'):
            args = self.parsed_opts_args[1].get(__option)
            args = (True if args is not None and not args else args)
            return args
        elif __option.startswith('-'):
            __option = (_sort_str(__option[1:]) if sorted_comparison else __option)
            for opt, args in self.parsed_opts_args[0].items():
                if opt is None:
                    continue
                if __option == (_sort_str(opt[1:]) if sorted_comparison else opt):
                    return True if not args else args
        else:
            raise _exceptions.ConfigError("option prefix `-' missing")

    def get_short_by_re(self, __re: Pattern | str) -> None | tuple[str, list]:
        """
        :return: ( -option, [args] )
        """
        if not self.parsed_opts_args:
            return
        for opt, args in self.parsed_opts_args[0].items():
            if opt is None:
                continue
            if search(__re, opt):
                return opt, args

    def _nopts_from_command(self, command: str) -> int | tuple:
        return list(self.config[command][1])[0]

    def _build_header(self, command: str) -> str:
        config = self.config[command]
        n_opts = self._nopts_from_command(command)
        return consoleparser._PRINTING.CMD_HEADER % (
            command,
            (n_opts if isinstance(n_opts, int) else n_opts[0]),
            (n_opts if isinstance(n_opts, int) else n_opts[1]),
            (consoleparser._PRINTING.FUNC_MAIN % config[0].__qualname__ if consoleparser.LOOKUP_FUNC and hasattr(config[0], '__qualname__') else "")
        )

    def _gen_opt_lns(self, command: str) -> dict:
        default = self.config[command][1].get(None)
        for opt, setsbox in self.config[command][1][self._nopts_from_command(command)].items():
            _opt = opt
            if opt is None:
                _opt = opt = ""
            opt_ln = {_opt: str()}
            if not opt.startswith('--'):
                opt = '-' + opt
            if not isinstance(setsbox, tuple):
                setsbox = (setsbox,)
            if default:
                if default.startswith('--'):
                    if opt == default:
                        opt_ln[_opt] += consoleparser._PRINTING.DEFAULT_OPTION % opt
                    else:
                        opt_ln[_opt] += consoleparser._PRINTING.OPTION % opt
                elif search(f"^{opt}$", default):
                    opt_ln[_opt] += consoleparser._PRINTING.DEFAULT_OPTION % opt
                else:
                    opt_ln[_opt] += consoleparser._PRINTING.OPTION % opt
            else:
                opt_ln[_opt] += consoleparser._PRINTING.OPTION % opt
            for mod in setsbox:
                if mod == 0:
                    break
                opt_ln[_opt] += consoleparser._PRINTING.ARG % mod
            yield opt_ln

    def _get_opt_lns(self, command: str) -> list:
        self._interception_key = None
        opt_lns = list(self._gen_opt_lns(command))
        interceptions = list(self.intercept_options)
        if consoleparser.LOOKUP_INTERCEPT:
            for opt_ln in opt_lns:
                i_opt = list(opt_ln)[0]
                if _opt := self._search_intercept((i_opt if i_opt.startswith('-') else '-' + i_opt)):
                    interceptions.remove(_opt)
                    opt_ln[i_opt] += consoleparser._PRINTING.INTERCEPT % self.intercept_options[_opt].__qualname__
        for _i_opt in interceptions:
            i_opt = _i_opt
            if not _i_opt.startswith('-'):
                i_opt = '-' + _i_opt
            opt_lns.append(
                {
                    _i_opt:
                        consoleparser._PRINTING.OPTION % i_opt + (
                            consoleparser._PRINTING.INTERCEPT % self.intercept_options[_i_opt].__qualname__
                                if consoleparser.LOOKUP_INTERCEPT
                                else ""
                        )
                }
            )
        return opt_lns

    def _build_lookup(self):
        self.look_up = dict()
        self.cmd_look = ""
        cmd_look = ""
        for command, config in self.config.items():
            self.look_up[command] = ["", dict()]
            self.look_up[command][0] += self._build_header(command)
            for opt in self._get_opt_lns(command):
                self.look_up[command][1] |= opt
            if len(cmd_look) >= consoleparser._PRINTING.CMD_LOOK_LN_MAX_CARS:
                self.cmd_look += cmd_look.strip() + "\n"
                cmd_look = ""
            cmd_look += consoleparser._PRINTING.CMD % command
        if cmd_look:
            self.cmd_look += cmd_look.strip()
        self.cmd_look = self.cmd_look.strip()

    def get_look_up(self, exception: Exception = None, full: bool = False) -> str:
        look_up = ""
        if exception:
            look_up += consoleparser._PRINTING.EXP % exception
        if not self.look_up:
            self._build_lookup()
        if full:
            for cmd, args in self.look_up.values():
                look_up += "%s\n" % cmd
                for arg in args.values():
                    look_up += "%s\n" % arg
            return look_up.strip()
        if not self.command:
            look_up += self.cmd_look
            return look_up.strip()
        cmd, args = self.look_up[self.command]
        look_up += "%s\n" % cmd
        for arg in args.values():
            look_up += "%s\n" % arg
        return look_up.strip()

    def _snake_func(self, *args, **kwargs) -> None:
        pass

    def add_command(self, command: str, __func: Callable = None) -> None:
        """
        add a command
        """
        if __func is None: __func = self._snake_func
        self._conf_curcmd = command
        self.config[command] = (__func, {0: {}})

    def _get_setsbox_conf(self, command: str = None):
        if command is None:
            command = self._conf_curcmd
        return list(self.config[command][1].items())[0]

    def _pop_default_conf(self, command: str = None):
        if command is None:
            command = self._conf_curcmd
        if default := self.config[command][1].get(None):
            self.config[command][1].pop(None)
        return default

    def _conf_command(self, command: str):
        if command is not None:
            self._conf_curcmd = command

    def add_n_opts(self, _form: int, to: int = None, command: str = None) -> None:
        """
        set the number of options that can be given
        """
        self._conf_command(command)
        setsbox_conf = self._get_setsbox_conf(self._conf_curcmd)
        n_args = setsbox_conf[0]
        self.config[self._conf_curcmd][1].pop(n_args)
        n_args = _form
        if to is not None:
            n_args = (_form, to)
        self.config[self._conf_curcmd][1][n_args] = setsbox_conf[1]
        if default := self._pop_default_conf():
            self.config[self._conf_curcmd][1][None] = default

    def add_command_opt_setsbox(self, option: Pattern | str | None, *typing_box: _ArgLetter, command: str = None) -> None:
        """
        :param option:
        - long options declared with prefix '--';
        - short options are [compiled (only for highlighting)] re-pattern
        :param typing_box: Amount, type and syntax of arguments
        :param command: where added to
        """
        if not self._debug:
            eol = False
            opt = False
            for n, arg_letter in enumerate(typing_box):
                if eol:
                    raise _exceptions.ConfigError(f"{option}: ArgLetter={arg_letter} after FinalArgLetter={typing_box[n - 1]}")
                if opt and int(arg_letter) > 0:
                    raise _exceptions.ConfigError(f"{option}: StaticArgLetter={arg_letter} after OptionalArgLetter={typing_box[n - 1]}")
                if int(arg_letter).bit_length() in (2, 3):
                    eol = True
                if int(arg_letter) < 0:
                    opt = True
        option = (option.pattern if isinstance(option, Pattern) else option)
        self._conf_command(command)
        setsbox_conf = self._get_setsbox_conf(self._conf_curcmd)
        n_args = setsbox_conf[0]
        if not n_args:
            n_args = 1
            self.add_n_opts(n_args)
        if len(typing_box) == 1:
            typing_box = typing_box[0]
        elif not typing_box:
            typing_box = 0
        self.config[self._conf_curcmd][1][n_args][option] = typing_box

    def add_default(self, option: str, command: str = None) -> None:
        """
        set a default option if none is selected
        """
        self._conf_command(command)
        if not option.startswith('-'):
            raise _exceptions.ConfigError("option prefix `-' missing")
        self.config[self._conf_curcmd][1][None] = option

    def add_interception(self, option: str, __func: Callable | tuple[str, Callable]) -> None:
        """
        - Add an interception at `option'.
        - `__func' gets the parser when called.
        - raises `Interception', initialized with the return value of `__func', after execution.
        :param option: interception at option; "--longopt" | "short-opt-re"
        :param __func: callable | tuple["keyword_for_parser", callable]
        """
        self.intercept_options |= {option: __func}

    def help(self, _):

        page = ""

        def hasselectedopt():
            if self.selected_opts_args:
                if _opt.startswith('--'):
                    return _opt in self.selected_opts_args
                for _o in self.selected_opts_args:
                    if search(f"-{_opt}", _o):
                        return True

        def opt_index():
            for __i, _o in enumerate(options):
                _o = list(_o)[0]
                if _o == _opt:
                    return __i, _o

        def final():
            nonlocal page
            for opt_ln in options:
                _ln = list(opt_ln.values())[0]
                if not _ln.endswith('\n'):
                    _ln += '\n'
                page += _ln
            raise _exceptions.Help(page.strip())

        if self.command:
            page += self._build_header(self.command) + "\n"
            options = list(self._get_opt_lns(self.command))
            if self.open_man:
                with self.open_man() as f:
                    while ln := f.readline():
                        if search(f"^\$\$\$%\({self.command}\)", ln):
                            while not search("^\$\$\$%|^\s\s\$\$%", ln := f.readline()):
                                page += ln
                            if ln.startswith("$$$"):
                                final()
                            while ln:
                                while not (m := search("(^\s\s\$\$%\(|^\$\$\$%\().+(?=\)($|\s))", ln)) and ln:
                                    ln = f.readline()
                                if ln.startswith("$$$"):
                                    final()
                                _opt = sub("^\$\$\$%\(|^\s\s\$\$%\(", "", m.group())
                                if hasselectedopt():
                                    _i, o = opt_index()
                                    options[_i][o] += "\n"
                                    while not search("^\$\$\$%|^\s\s\$\$%", ln := f.readline()):
                                        options[_i][o] += ln
                                    if ln.startswith("$$$"):
                                        final()
                                else:
                                    ln = f.readline()
                            final()
        raise _exceptions.Help(self.get_look_up(full=False))
