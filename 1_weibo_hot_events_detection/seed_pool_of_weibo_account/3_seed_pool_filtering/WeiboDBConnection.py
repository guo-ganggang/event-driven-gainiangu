import MySQLdb

def getDBConnection():
    try:
        con = MySQLdb.connect(host = "123.56.187.168", user = 'root', passwd ='Lifelabmaster2015', db='FinancialWeibo',port=3306, charset='utf8')
        # con = MySQLdb.connect(host = "127.0.0.1", user = 'root', passwd ='123456', db='tianyancha',port=3306, charset='utf8')
        return (con,con.cursor())
    except MySQLdb.Error:
        raise