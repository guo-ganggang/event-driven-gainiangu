import MySQLdb

def getDBConnection():
    try:
        con = MySQLdb.connect(host = "127.0.0.1", user = 'root', passwd ='123456', db='stockweibo',port=3306, charset='utf8')
        return (con,con.cursor())
    except MySQLdb.Error:
        print 'error....'
        raise