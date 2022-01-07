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

from ssl import SSLError
from socket import gaierror
from smtplib import SMTPAuthenticationError
from os import urandom

FILE_CREATED = "## File `%s' created"
SEPARATOR64 = "#" + ("=" * 64)

TOADD_USERLINE = \
    """## Make sure that at least the first column of the top line is present in 
`%s'"""
CLIENT_PEPPERS = \
    """## The following configuration must be done on the client side 
`%s'"""
PAIRING_INTR = \
    """## Pairing instruction:

     Host.py PROVIDED_PARING_IP '"0.0.0.0"' PROVIDED_PARING_USER '"%s"'
     Client.py DO_PAR True USER '"%s"'"""

Q_SAVE_USERLINE = \
    """## Should the line be added to 
`%s'?"""
Q_OVERWRITE = \
    """## These line(s) were found in 
`%s', 
should they be overwritten?"""
Q_SAVE = "## Should the configurations be written to a file?"
Q_TEST_MAIL = "## Wold you like to test the MailAlert?"
Q_SSL_ENCRYP = "## Should `SSL_KEY_FILE' be encrypted?"
Q_SSL_LOOKUP = "## CertLookup?"
Q_EXEC = "## Execution?"

MAIL_EXCEPTION = {
    UnicodeEncodeError: """
[ERROR]  An error occurred during the encoding of the password, this indicates a bad seed.
(MAIL_XFSEED  MAIL_FSC)
    """,
    ConnectionRefusedError: """
[ERROR]  The connection is not accepted by the server, check the port number.
(MAIL_SMTP_PORT)
    """,
    SSLError: """
[ERROR]  The authentication method is not supported by the server, try another value.
(MAIL_CRYPT)
    """,
    gaierror: """
[ERROR]  There were problems with the name resolution of the server address, please check it.
(MAIL_SMTP_ADDR)
    """,
    SMTPAuthenticationError: """
[ERROR]  The connection to the server could be established, but the login failed. 
Please check the username and make sure that the key file was created with the correct password. 
Note that some providers have special passwords for mail programs.
(MAIL_XF)
    """,
    None: """
[ERROR]  An unexpected error occurred.
"""
}
ERR_CORRESPONDING_VAL = "[WARNING] `%s': <could not get the value corresponding to \n`%s'>"
ERR_FILE_NOT_FOUND = "[ERROR]  FileNotFoundError: `%s'"

SSL_CMDLN = "%s req -new -x509 -out %s -keyout %s -config %s %s -days 365"
SSL_PASS_OUT = "-passout pass:%s"
SSL_NODES = "-nodes"

SSL_LOOKUP = "%s x509 -in %s -text"

ERR_SSL = {
    1: """
    [OpenSSL could not be found] 
    If apt is used as the packet management interface, 
    OpenSSL can be installed using the following command.
    <sudo apt install openssl>
    """,
    2: """
    The links below will take you to a great project that will help you 
    conveniently install openssl on Windows. The files are not provided by the 
    author on a popular platform, so the browser will probably resist 
    downloading the files at first. After running the selected installer, 
    start.bat can be executed in the installed directory to create a terminal 
    in which the openssl command can be executed.

    Shining Light Productions - OpenSSL Installer : 
        https://slproweb.com/products/Win32OpenSSL.html
    Direct download link to the 64-bit version : 
        https://slproweb.com/download/Win64OpenSSL-3_0_1.exe
    -------------------------------------------------------------------    
    Or OpenSSL will be built from the sources. 

    Git - Welcome to the OpenSSL Project : 
        https://github.com/openssl/openssl#readme
    Git - OpenSSL - Build from Sources - Win Notes : 
        https://github.com/openssl/openssl/blob/master/NOTES-WINDOWS.md
    """,
    4: """
    [An error occurred during execution] 
    Possibly the configuration file is not suitable for execution 
    through this interface. If the file has been modified, make 
    sure that it contains the following signature.
    
    [ req ]
    prompt = no
    distinguished_name	= req_distinguished_name
    ...
    [ req_distinguished_name ]
    stateOrProvinceName		= STD
    ...
    
    Otherwise the files can be created manually.
    """
}

_MAIL_TEST = (r"""
         
          ___   _      ___   _      ___   _      ___   _      ___   _
         [(_)] |=|    [(_)] |=|    [(_)] |-|    [(_)] |=|    [(_)] |-|
          '-`  |_|     '-`  |_|     '-`  |_|     '-`  |_|     '-`  |_|
         /mnm/  /     /mmm/  /     /mnm/  /     /mmm/  /     /mbm/  /
               |____________|_____________|____________|____________|
                                     |            |            |
                                 ___  \_      ___  \_      ___  \_
                                [(_)] |=|    [(_)] |-|    [(_)] |=|
                                 '-`  |_|     '-`  |_|     '-`  |_|
                                /mnm/        /mnm/        /mnm/


""", r"""
        ---=---+---=---
               \___
         ----=---+-I-=----
                |\
          ----=----+----=----
                |
                ^


""", r"""
       , ___
     `\/{o,o}
      / /)  )
     /,--"-"-


""", r"""


                  +     /\        *
             '        /   |    
        .            / /| | .  
              *   .,--,. /     
                 /      /|     
          ,      \ ,   / /    ´
                 /\_../-'      
       *      , / |/ /         *
               /    / o        
          .    /  /             .
               '''     +       
            *               *
            
            
""", r"""


               |
             \|/|/
           \|\\|//|/
            \|\|/|/
             \\|//
              \|/
              \|/
               |
         _\|/__|_\|/____\|/__
         
""", r'''


         / .'
   .---. \/
  (._.' \()
   ^"""^"

''', r"""


          /
       -=<=-< * * * * * * * * * * * *
          \
          
          
""", r"""


                          ____
 ________________________/ O  \___/
<%%%%%%%%%%%%%%%%%%%%%%%%_____/   \


"""
              )

MAIL_ALERT_TEST = _MAIL_TEST[ord(urandom(1)) % len(_MAIL_TEST)]

MANUALS = {
    'man': """
    man - The interface to call the manual pages of the configuration attributes

OPTIONS/ARGUMENTS

    index   : Print the index and exit.
    <n>     : Output the manual page on index <n> and exit.
    <name>  : Output the manual page to <name> and exit. 
              If the desired name is capitalized throughout, it need not be <name>.
""",
    'login': """
    login - Creation of a new user

OPTIONS

    login : Create only the key files for `USER'.
    files : Start only the configuration interface 
            for the files configuration.
""",
    'mail': """
    mail - Creation of the MailAlert

OPTIONS

    server : Start only the configuration interface for the server 
             configuration.
    key    : Create only the key files for `USER'.
    test   : Test MailAlert, start the configuration interface if 
             configurations are missing.
""",
    'sheet': """
sheet - Creates a configuration file

OPTIONS

    defaults    : Start the default runtime configuration process and 
                  write the sheet with the default values.
    host        : Start the runtime configuration process for `Host.py' 
                  and write the sheet with the default values.
    client      : Start the runtime configuration process for `Client.py' 
                  and write the sheet with the default values.
    lateral     : Start the runtime configuration process for the lateral 
                  scripts and write the sheet with the default values.
""",
    'ssl': """
    ssl - The interface to create the SSL certificate functionally

OPTIONS/ARGUMENTS

    -
""",
    'help': """
    SefiTrash - Config - Command line interface

The interface offers the possibility to do some more complex configurations of SefiTrash via command line.

  - If it makes sense for the configuration, the user and a 
    configuration file are queried in the first instance.

  - Required attributes are marked with '*' when entering values.
  - When entering passphrases, the prompt starts with `!' 
    (the input is not displayed)
  - Default values are shown in square brackets `[]' and are used 
    if the input is left empty.
  
FUNCTIONS

    man     : The interface to call the manual pages of the configuration attributes
    sheet   : Creates a configuration file
    ssl     : The interface to create the SSL certificate functionally
    login   : The creation of a new user
    mail    : Creation of the MailAlert

Most functions accept an option or an argument, run `<function>?' to know more.

INFO

    help        : Print this page.
    SefiTrash   : Output the cover page of the project.
    !			: Same as SefiTrash
    <function> help : Output the manual page for the <function>.
    <function> ?	: Same as `<function> help'

SYNOPSYS

    <function> [option] [argument]

    Can be done from the command line:

    Config-cli.py <function> [option] [argument]
"""
}

MANUALS[None] = MANUALS['help']
