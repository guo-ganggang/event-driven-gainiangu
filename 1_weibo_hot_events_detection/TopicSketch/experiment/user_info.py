__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import MySQLdb
import json

_user_info = dict()


_connection = MySQLdb.connect(host='?', user='?', db='?', charset='utf8', passwd='?')
print 'successful connection for user info!'
_cursor = _connection.cursor()

_cursor.execute('select id, json from users')
_row = _cursor.fetchone()
while _row:
    uid = _row[0]
    obj = eval(_row[1])
    _user_info[uid] = obj
    _row = _cursor.fetchone()

print 'in all ' + str(len(_user_info)) + ' users.'
_cursor.close()
_connection.close()

print 'connection closed for user info!'


def get_user(uid):
    if uid in _user_info:
        return _user_info[uid]
    else:
        return None

