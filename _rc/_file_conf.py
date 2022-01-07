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


from sys import platform as _sys_platform
from re import sub as _re_sub

if _sys_platform == "win32":
    main_root = _re_sub("\\\[^\\\]+\\\[^\\\]+$", "", __file__)
else:
    main_root = _re_sub("/[^/]+/[^/]+$", "", __file__)


########################################################################################################################
# ETC
########################################################################################################################

board_path_rule = main_root + '/etc/BOARD_paths.txt'
board_client_rule = main_root + '/etc/BOARD_clients.txt'
board_call_rule = main_root + '/etc/BOARD_calls.txt'
board_users = main_root + '/etc/BOARD_users.txt'

########################################################################################################################
# Logfiles
########################################################################################################################

log_firewall = main_root + '/var/log/classified/Firewall.log'
log_call = main_root + '/var/log/classified/Call.log'
logpath_toxic_data = main_root + '/var/log/classified/toxic.dat/'

log_path = main_root + '/var/log/bridge/Path.log'
log_bridge = main_root + '/var/log/bridge/Bridge.log'
log_remote = main_root + '/var/log/bridge/remote.log'

# _special usage_
log_basic_file = None
log_kill = main_root + '/var/log/blackbox/Z0.log'          # Needed for the restart after the kill.
log_sockio = main_root + '/var/log/blackbox/SockIO.log'
log_blackbox = main_root + '/var/log/blackbox/BLACKBOX.log'
log_logstreamerr = main_root + '/var/log/blackbox/LogStreamErr.log'  # Not observed by file, stream or backup handlers.

########################################################################################################################
# SSL
########################################################################################################################

ssl_cert_file = main_root + '/var/ssl/ca.pem'
ssl_key_file = main_root + '/var/ssl/ca.key'


########################################################################################################################
########################################################################################################################


########################################################################################################################
# LOGIN FILES
########################################################################################################################

fsc_host_spice_file = main_root + '/var/internal/%s.xf-spc'
fsc_host_xf = main_root + '/var/internal/%s.xf-lin'
fsc_host_table_file = main_root + '/var/internal/%s.xf-hst'
fsc_pepper_host = main_root + '/var/internal/_%s.xf-ppp'
fsc_establish_pepper = main_root + '/var/internal/-%s.xf-ppp'
fsc_establish_table_file = main_root + '/var/internal/-%s.xf-hst'

mail_xf = main_root + '/var/internal/%s.xf-mli'

########################################################################################################################
# BRIDGE SRC / DST
########################################################################################################################

src_basic_root = ''
dst_basic_root = ''