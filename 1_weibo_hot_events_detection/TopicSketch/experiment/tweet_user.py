__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import MySQLdb


def get_user_icon(uid):
    connection = MySQLdb.connect(host='?', user='?', passwd='?', db='sina_weibo')

    ret = None

    cursor = connection.cursor()
    cursor.execute("select profile_img_url from weibo_users where uid = '" + str(uid) + "'")
    row = cursor.fetchone()

    if row is None:
        cursor = connection.cursor()
        cursor.execute("select fer_profile_img_url from weibo_followers where fer_uid = '" + str(uid) + "'")
        row = cursor.fetchone()

    if row is None:
        cursor = connection.cursor()
        cursor.execute("select fee_profile_img_url from weibo_followees where fee_uid = '" + str(uid) + "'")
        row = cursor.fetchone()

    if row:
        ret = row[0]

    return ret