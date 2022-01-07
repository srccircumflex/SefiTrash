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


# consequences (prefabricated) #########################################################################################

# provided consequence for (D)DOS pattern and maximal verification attempt
# v— 0s to 255s
_sleep1: str = 'from os import urandom; from time import sleep; sleep(ord(urandom(1)))'

# provided consequence for (D)DOS pattern and maximal verification attempt
# v— 240s to 1275s
_sleep2: str = 'from os import urandom; from time import sleep; sec = urandom(2);sleep((ord(sec[0])' \
                                ' if ord(sec[0])>60 else 60) + (ord(sec[1])*3 if ord(sec[1])>60 else 180))'

# provided consequence for (D)DOS pattern and maximal verification attempt
# v— 720s to 1785
_sleep3: str = 'from os import urandom; from time import sleep; sec = urandom(2);sleep((ord(sec[0])' \
                                ' if ord(sec[0])>120 else 120) + (ord(sec[1])*6 if ord(sec[1])>100 else 600))'

# provided consequence for (D)DOS pattern and maximal verification attempt
_shutdown = 'raise OverflowError'

# provided consequence for maximal verification attempt
_ban: str = 'raise PermissionError'

class sleep1:
    max_bad_clients_exec_lv1 = _sleep1
    max_bad_clients_exec_lv2 = _sleep1
    max_bad_clients_exec_lv3 = _sleep1
    max_bad_client_hit_exec_lv1 = _sleep1
    max_bad_client_hit_exec_lv2 = _sleep1
    max_bad_client_hit_exec_lv3 = _sleep1
    max_unverified_exec_lv1 = _sleep1
    max_unverified_exec_lv2 = _sleep1
    max_unverified_exec_lv3 = _sleep1

class sleep2:
    max_bad_clients_exec_lv1 = _sleep2
    max_bad_clients_exec_lv2 = _sleep2
    max_bad_clients_exec_lv3 = _sleep2
    max_bad_client_hit_exec_lv1 = _sleep2
    max_bad_client_hit_exec_lv2 = _sleep2
    max_bad_client_hit_exec_lv3 = _sleep2
    max_unverified_exec_lv1 = _sleep2
    max_unverified_exec_lv2 = _sleep2
    max_unverified_exec_lv3 = _sleep2

class sleep3:
    max_bad_clients_exec_lv1 = _sleep3
    max_bad_clients_exec_lv2 = _sleep3
    max_bad_clients_exec_lv3 = _sleep3
    max_bad_client_hit_exec_lv1 = _sleep3
    max_bad_client_hit_exec_lv2 = _sleep3
    max_bad_client_hit_exec_lv3 = _sleep3
    max_unverified_exec_lv1 = _sleep3
    max_unverified_exec_lv2 = _sleep3
    max_unverified_exec_lv3 = _sleep3

class shutdown:
    max_bad_clients_exec_lv1 = _shutdown
    max_bad_clients_exec_lv2 = _shutdown
    max_bad_clients_exec_lv3 = _shutdown
    max_bad_client_hit_exec_lv1 = _shutdown
    max_bad_client_hit_exec_lv2 = _shutdown
    max_bad_client_hit_exec_lv3 = _shutdown
    max_unverified_exec_lv1 = _shutdown
    max_unverified_exec_lv2 = _shutdown
    max_unverified_exec_lv3 = _shutdown

class ban:
    max_unverified_exec_lv1 = _ban
    max_unverified_exec_lv2 = _ban
    max_unverified_exec_lv3 = _ban