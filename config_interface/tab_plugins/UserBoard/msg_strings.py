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

QUICK_GUIDE = """
Quick guide of the login creation
  - Press -Fill- in the [Values] menu or <Ctrl-F>
  - Fill the first input of the line with the name of the user
  - Press with the mouse on the input field while holding <Ctrl>
  
To complete the configuration, the user line must be created in `BOARD_USERS'.

"""

DESCRIPTION = """
----------------------------------------------------------------------------------------------------------------------------------------
[Username input] | half life: [Seconds input] | laps lim: [Limit input] | [01] laps del | [(FSC-Peppers input)] | [01] del flag | row-id
----------------------------------------------------------------------------------------------------------------------------------------

This interface supports the creation and editing of `BOARD_USERS'.
The standard values can be loaded via <Ctrl-F>, then the file can be read in by pressing the Source File button (upper path input right side). 
After editing, the file defined in the lower path input is written by pressing the Write Out button ( leftmost side). Optionally, 
the peppers can be excluded and written to a separate file (rightmost).
In the upper right corner, a line can be added (automatically by navigating with <Tab>), the values of all lines can be checked or 
all the lines marked by the <del> flag can be removed. The key button creates interfaces for creating logins for all loaded user rows.

half life: Lifetime in seconds
laps lim: Limit for expired logins in runtime
laps del: Boolean to define if a user line is marked with the <del> flag on expired login
Peppers: <initalvector> <chipher-stream-part> <part-priority> <transpossiton-hops>

FILE DESCRIPTION

  Defines registered users and some arguments. The arguments can be omitted in the file to refer
  to the associated constant (`lft' `lpl' `lpd' / `FSC_XF_LIFETIME' `LAPSLOGIN_LIM_RUNTIME'
  `LAPSLOGIN_DEL') or to query on stdio (`bpp').
"""


PASS_ENTRY = \
    """Enter the passphrase, then press <Return>"""

ERR_CONF_REQ = """
RowID=%d
[ERROR] these values must be set in the main tab:
  %s
  %s
  %s
  %s
  %s
[ERROR] one of these values must be set:
  `%s' in the main tab or
  `%s' in the user line
[ERROR] `%s' must be set
(Use -Fill- in the [Value] menu)
"""

PAIRING_INSTR = """
Pairing instruction:

  Host.py <Pairing Args>
  Client.py DO_PAR True USER '"<Username>"'

Note that the configuration of `BASIC_FSC_PEPPER' on the client side matches the one in the user line on the host side
------------------------------------------------------------------------------------------------------------------------------------------------
"""

EXCEPTION = \
    """[EXCEPTION]: %s
"""

SEPARATOR128 = """
=================================================================================================================================================
"""

INSERTED_INTO = """
Inserted into: %s
Peppers included: %s
================================================================================================================================================

"""

INSERTED_INTO_P = """
Inserted into: %s
================================================================================================================================================

"""

INSERT = \
    """Insert - %s
"""

CREATED = """
Created: %s
Peppers included: %s
================================================================================================================================================

"""

CREATED_P = """
Created: %s
Peppers included: %s
================================================================================================================================================

"""

WRITE = \
    """Write - %s
"""

WRAP84 = """
=======================================================================
%s
=======================================================================
"""

WRAP32 = """
================================
%s
================================
"""

WRAP32ASK = """
================================
%s
================================

Cancel further processing ?
"""

ERR_TITLE = \
    """%d : [ERROR]"""

ERR_PASS = """
Enter the passphrase
"""

LOGIN_CREATED = \
    """[LOGIN CREATED] %-19s %-12s (Pairing Args=<PROVIDED_PARING_IP '"0.0.0.0"' PROVIDED_PARING_USER '"%s"'>)
"""

GETTING_LINES = """
=================================================================================================================================================
RECEIVED LINES
=================================================================================================================================================
"""

GET_LINE = \
    """Get : %s
"""

BREAK = """
================================================================================================================================================
                                                            [BREAK]
================================================================================================================================================
"""

label_passph = "Passphrase:"
#               [                       ]
label_filecf = "File config:"
def label_fileln(auth_cnf):
    return ["  %s - %s" % item for item in auth_cnf.items()
            if item[0] != 'bpp']
label_encodi = "Encoding:"
label_encovl = "  %s"
label_pepper = "Peppers:"
label_peppvl = "  bpp - %s"

