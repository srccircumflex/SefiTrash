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

DESCRIPTION: str
DESCRIPTION_B: str

LIN_DESCR = """This interface provides support for the correct creation of the ssl 
certificate and the key file.

The upper entries describe the command to be executed and after pressing 
<Ctrl-F> no further processing is required. Many commands of Openssl use 
an external configuration file, this can be edited freely on the left side.
To avoid the query of stdin the section '[ req ]' and the line 'prompt=no' 
in it is mandatory. To load the backup configuration file press <Alt-Shift-R> 
while the cursor is in the field. The processing is started by pressing the 
arrow button.
"""

WIN_DESCR = LIN_DESCR + """
Processing will output the required command line. 

The links below will take you to a great project that will help you 
conveniently install openssl on Windows. The files are not provided by the 
author on a popular platform, so the browser will probably resist 
downloading the files at first. After running the selected installer, 
start.bat can be executed in the installed directory to create a terminal 
in which the openssl command can be executed.

Or OpenSSL will be built from the sources. 
"""

NO_ACCESS = LIN_DESCR + """
Processing will output the required command line.

To create the files directly execute the command below in the terminal 
and restart `Config-tk.py'.
"""

LIN_DESCR += """
The successful completion is marked by  +++ exit 0 +++. 
"""

WIN_DESCR_B = """
    Shining Light Productions - OpenSSL Installer  : https://slproweb.com/products/Win32OpenSSL.html
    Direct download link to the 64-bit version     : https://slproweb.com/download/Win64OpenSSL-3_0_1.exe
    ----------------------------------------------------------------------------------------------------------------
    Git - Welcome to the OpenSSL Project           : https://github.com/openssl/openssl#readme
    Git - OpenSSL - Build from Sources - Win Notes : https://github.com/openssl/openssl/blob/master/NOTES-WINDOWS.md
"""

LIN_DESCR_B = \
    """"""

NO_ACCESS_B = """
  sudo apt install openssl
"""

SEPARATOR128 = \
    """================================================================================================================================
"""

COMMAND_PRINT = """
  Create ssl files : 
    %s
    
  Lookup command   : 
    %s

"""

ERR = \
    """[ERROR] %s
"""

