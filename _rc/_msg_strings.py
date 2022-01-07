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


class STRINGS:
    KILL_THREAD = "KILLING THREAD"
    KILL_BACKUP = "BACKUP WRITEN"
    KILL_LOG = " # %s # %s # %s"

    PORT_INIT = "NO AVAILABLE PORT IN RANGE %s"

    LISTENER = "LISTENER ESTABLISHED AT %s:%d"
    NEW_SESSION = "%s"
    REC_CONNECTION = "CONNECTION RECEIVED FROM %s"
    FW_PASSED = "FirewallPassed"
    LISTENER_CLOSE = "LISTENER CLOSED"

    CALL_DROP = "%s"
    CALL_LIM = "LIM: <%s%s>"
    CALL_REQ = "CallRequest from %s, Wrapper: %s"

    ENDIF = "%s isn't configured"

    IP = "%s NotOnBoard"
    OVERFLOW = "Overflow:"
    IP_BOARD_PASSED = "IPBoard: %s Passed, Wrapper: %s"
    FW_AUTO_RESET = "FirewallAutoReset@%d born@%d"

    DOS = "%s / potential DOS \\ level %d/3"
    DDOS = "%s / potential DDOS \\ level %d/3"
    TOX = "ToxicDataLogger enabled"
    LOGIN_LV = "LoginLimit %d/3"
    UNVERIFIED = "UnverifiedClient"

    LOGIN = "LOGIN from %s"
    LOGIN_LAPSED = "LOGIN LAPSED"

    BRIDGE = "Bridge initialled for %s"
    BRIDGE_CLOSED = "Bridge closed"

    SECUREPATH = "SecurePath initialled for %s"

    SENDER_ON = "SenderGate"
    SENDER_CON = "SENDER CONNECTED TO %s"
    SENDER_OFF = "SenderGate"
    CLOSE_GW_FLAG = "CloseGateWaysFlag received"
    SHUTDOWN = "SHUTDOWN"

    PROVIDE_PAR = "PROVIDED: %s"
    PAR_REQ = "¿ %s ?"
    PARED = "%s PARED"

    SEND_PINGS_TO = "SendPings ··· %s  (interrupt^C to continue)"
    PINGS_SEND = "PingsSend"
    NO_REC_PORT = "NoReceivedPort - range: %s"
    NO_REC_PORT_FIN = "NoReceivedPort - IPS: %s"

    HANDSHAKE_TIMEOUT = "waiting for handshake"
    NO_REC_HANDSHAKE = "NoReceivedHandshake"

    PIPE_PROVIDED = "PIPE provided"
    BRIDGE_PROVIDED = "BRIDGE provided"
    INTERVENT_AT = "BYPASS @ %s:%d"
    INSPECTTRM_AT = "LOG-STREAM @ %s:%d"
    INTERVENT_CON = "INTERVENT %s:%d"
    INSPECTTRM_CON = "INSPECT %s:%d"

    NOTGETTING = "Could not get: %s"

    fe_INVALID_PART = "InvalidPairingPart <%s>"
    fe_WRONG_LENGTH = "WrongLengthError"
    fe_TIMEOUT = "TimeoutError <%d>"
    fe_COMPANION = "WrongCompanion <exp:%s/rec:%s>"
    fe_USERNAME = "Username invalid. Use alpha-nums only [0-9a-zA-Z_]"

    fe_LOGIN_VERIFY = "[!*] LoginVerificationError - failed"
    fe_HANDSHAKE = "[!*] LoginHandshakeError - failed"
    fe_NO_LOGIN = "[?] NoLoginError"
    fe_NO_USER = "[?] NoUserError"
    fe_NO_NEW_LI = "[?] NoNewHashError"
    fe_NO_LLOGIN = "[?] NoLocalLoginError"
    fe_PEPPER = "[!] PepperDecryptionError - cast failed"
    fe_PEPPER2 = "[!?] PepperDecryptionError - few arguments"
    fe_TIMESTAMP = "[?] TimeStampLapsed <lim:%d/age:%d>"
    fe_CAST = "[!] % - cast failed"
    fe_KEY_MISSING = "[?] % - key missing"
    fe_TABLE = "[!] HandsTableDecryptionError - wrong index"
    fe_LAPSLIN_LIM = "[!] LapsedLoginLimitError"


LEVEL_TO_NAME = {
    61: 'ALERT',
    60: 'FATAL',
    55: 'COUNTER',
    54: 'PREVENT',
    50: 'CRITICAL',
    45: 'DEPTHERR',
    40: 'ERROR',
    35: 'HARD',
    30: 'WARNING',
    25: 'INIT',
    20: 'INFO',
    15: 'DATA-I',
    10: 'DEBUG',
    5: 'DATA-O',
    0: 'NULL'
}
