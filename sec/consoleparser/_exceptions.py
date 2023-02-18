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

class ConfigError(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)

class ParserException(ValueError):
    def __init__(self, *args):
        ValueError.__init__(self, *args)

class ParsError(ParserException):
    def __init__(self, *args):
        ParserException.__init__(self, *args)

class NoInputError(ParserException):
    def __init__(self, *args):
        ParserException.__init__(self, *args)

class UnknownCommandError(ParserException):
    def __init__(self, *args):
        ParserException.__init__(self, *args)

class Interception(Warning):
    def __init__(self, *args):
        Warning.__init__(self, *args)

class Help(Interception):
    def __init__(self, *args):
        Interception.__init__(self, *args)

