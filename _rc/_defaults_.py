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


from _rc._file_conf import *
from _rc._msg_strings import *
from _rc._exec_strings import *
from _rc._def_print import *

user = None
default_user = 'root'
ip_receiver = '127.0.0.1'
ip_local = '127.0.0.1'
port_range_receiver = (50000, 50000)
port_range_establish = (50020, 50030)
paring_lifetime = 30
sensitive_paring = False
intervent_ip = '127.2.4.8'
intervent_port = 1632
inspect_ip = '127.1.1.2'
inspect_port = 35813
ssl_password = None
basic_fsc_pepper = (61, (0, 1), 3)
fsc_xf_lifetime = 2764800
lapslogin_lim_runtime = 3
lapslogin_del = 1
timestamp_lifetime = 90
firewall_reset_interval = 86400
max_client_cache = 50
max_bad_clients_lv1 = 20
max_bad_clients_lv2 = 50
max_bad_clients_lv3 = 70
max_bad_clients_exec_lv1 = 'sleep2'
max_bad_clients_exec_lv2 = 'sleep3'
max_bad_clients_exec_lv3 = 'shutdown'
max_bad_client_hit_lv1 = 12
max_bad_client_hit_lv2 = 30
max_bad_client_hit_lv3 = 60
max_bad_client_hit_exec_lv1 = 'sleep1'
max_bad_client_hit_exec_lv2 = 'sleep2'
max_bad_client_hit_exec_lv3 = 'shutdown'
max_unverified_lv1 = 5
max_unverified_lv2 = 6
max_unverified_lv3 = 8
max_unverified_exec_lv1 = 'ban'
max_unverified_exec_lv2 = 'ban'
max_unverified_exec_lv3 = 'shutdown'
maxsize_toxics = 0
logmax_logsize = 10*1024*1024
logmax_backups = 3
loglv_firewall = [20, 30]
loglv_call = [30, 30]
loglv_path = [30, 30]
loglv_bridge = [20, 30]
loglv_kill = [30, 10]
loglv_sockio = [30, 30]
loglv_blackbox = [1, 60]
mailalertlv_blackbox = 61
mailalertlv_firewall = 55
mod_loglvto_debug = False
mod_loglvto_blackbox = False
mod_loglvto_alls = False
mod_loglvto_allf = False
mod_bgstream = None
mod_stream_readloop = True
print_timeout_bar = 'ordin'
print_icos = 'ordin'
print_stream_args = 'ordin'
print_intervention_onoff = 'ordin'
print_intervention_flush = 'ordin'
print_intervention_error = 'ordin'
dat_sock_buffer = 1024
dat_read_buffer = 1024*1024
dat_maxsize_header = 10
dat_max_stacks = 3
ping_timeout = .5
response_timeout = 50
response_timeout_adjust = .2
queue_timeout = .5
conreset_timeout = .5
kill_timeout = 2.0
listen_timeout = 2.0
srm_enc = 'utf8'
loc_enc = None
log_enc = None
shutdown_exco = (0, 1)
rc_file_lv1 = None
dir_stat_tags = {
        # 0: 'st_mode',   # permissions bits
        # 1: 'st_ino',    # (Inode@UNIX, FileIndex@WINDOWS)
        # 2: 'st_dev',    # device identifier
        # 3: 'st_nlink',  # number of hard links
        # 4: 'st_uid',    # user id
        # 5: 'st_gid',    # group id
        6: 'st_size',   # length
        7: 'st_atime',  # access time
        8: 'st_mtime',  # modification time
        9: 'st_ctime'   # (MetadataChangeTime@UNIX, CreationTime@WINDOWS)
}
dir_time_form = "%y.%m.%d-%H:%M"
mail_smtp_addr = False
mail_smtp_port = False
mail_crypt = None
mail_user = None
mail_sender_mail = False
mail_receiver_mail = None
mail_bcc = None
mail_xfseed = None
mail_fsc = None
mod_login_to_alert = False
bypass_ip = None
bypass_port = None
bypass_cli_ip = None
bypass_cli_port = None
mod_set_bypass = False
