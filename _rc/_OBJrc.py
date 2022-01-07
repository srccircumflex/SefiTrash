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


import ssl
from os import access
from sec.fscIO import pph
from _rc import configurations


def _getsslpass():
    if configurations.SSL_PASSWORD is None:
        configurations.SSL_PASSWORD = pph("[PEM] Enter sha256 seed: ")
    return configurations.SSL_PASSWORD


if not configurations.LATERAL_:

    # SSL CONTENTS

    configurations._SSL_CONT_RECEIVER = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    configurations._SSL_CONT_RECEIVER.load_cert_chain(
        configurations.SSL_CERT_FILE,
        configurations.SSL_KEY_FILE,
        _getsslpass
    )

    configurations._SSL_CONT_SENDER = ssl._create_unverified_context()

    if configurations.HOST_SIDE and access(configurations.MAIL_XF % configurations.USER, 4):
        if configurations.MAIL_CRYPT in ('tls', 'ssl'):
            configurations._MAIL_SSL = ssl.create_default_context()
            configurations.MAIL_CRYPT = configurations.MAIL_CRYPT.upper()
        elif configurations.MAIL_CRYPT in ('TLS', 'SSL'):
            configurations._MAIL_SSL = ssl._create_unverified_context()
        else:
            exit("ConfigurationError: MAIL_XF without MAIL_CRYPT")


if (configurations.LATERAL_ or configurations.CLIENT_SIDE) and configurations.BYPASS_IP and configurations.BYPASS_PORT and configurations.BYPASS_CLI_IP and configurations.BYPASS_CLI_PORT:
    from sec.Bypass import ByPassj
    configurations._BYPASS = ByPassj()
    if configurations.MOD_SET_BYPASS: configurations._BYPASSED = configurations._BYPASS
