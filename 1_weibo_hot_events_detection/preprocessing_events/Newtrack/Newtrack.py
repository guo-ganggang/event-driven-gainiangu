import time

from datetime import datetime, date, timedelta as td

#import MySQLdb, redis
import pymysql
import redis
import json

#import topic_sketch.stream as stream

import stream

from collections import deque

#from timeout import timeout

#import exp_config

#import twokenize


_KEY_EVENT_CHANNEL = 'twitter:sg:event:python:weibo:ab_test:a'
_KEY_EVENT_PREFIX = _KEY_EVENT_CHANNEL + ':'
_KEY_EVENT_KEYWORDS = _KEY_EVENT_PREFIX + 'keywords'
_KEY_EVENT_KEYWORDS_TRACK2 = _KEY_EVENT_PREFIX + 'track2'

class Crawler:

    def __init__(self, start, end):
        self.deq = deque([])

        self.start = start

        self.end = end

        self.delta = td(seconds=10)

        self.lag = td(minutes=2*60 + 30)

        self.host = '10.0.109.33'
        self.user = 'clear'
        self.db = 'clear'
        self.charset = 'utf8'

        self.gap = None

        self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset, passwd='ClearDataBase2017^')
        cursor = self.connection.cursor()
        cursor.execute("desc timelines2")
        id = 0
        self.id_map = {}
        for column in cursor.fetchall():
            self.id_map[column[0]] = id
            id += 1
        # cursor.close()

    def checkTime(self, end):
        sql_str = 'select TIMESTAMPDIFF(second, "%s",max(created_at)) as gap from clear.timelines2;' % (end);
        cursor = self.connection.cursor()
        cursor.execute(sql_str)
        ret = cursor.fetchone()
        print('time gap is ', ret[0])
        return ret[0]

    #@timeout(60*10)
    def range(self, t_start, t_end):
        _time0 = t_start.strftime("%Y-%m-%d %H:%M:%S")
        _time1 = t_end.strftime("%Y-%m-%d %H:%M:%S")

        if self.gap is None:
            print('check time for %s' % (_time1))
            self.gap = self.checkTime(_time1)/10

        while self.gap < 0:
            print('max time less than end time!!!!!! sleep 30 seconds.')
            time.sleep(30)
            self.gap = self.checkTime(_time1)/10

        try:
            # print('closing old connection...')
            # self.connection.close()
            print( 'sleep 2 seconds')
            time.sleep(2)
            # print( 'trying to reconnect db ...')
            # self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset,passwd='clear')
            print( 'successful connection!')
            cursor = self.connection.cursor()
            sql_str = 'select text, created_at from ' + 'timelines2' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
            print(sql_str)
            cursor.execute(sql_str)
            ret = cursor.fetchall()
            # cursor.close()
        except:
            print('something wrong in DB.')
            print( 'sleep 1 seconds')
            time.sleep(1)
            print('closing old connection...')
            self.connection.close()
            print( 'trying to reconnect db ...')
            self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset,passwd='ClearDataBase2017^')
            cursor = self.connection.cursor()

            sql_str = 'select text, created_at from ' + 'timelines2' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
            print(sql_str)

            cursor.execute(sql_str)
            ret = cursor.fetchall()

        self.gap -= 1
        return ret




    def load(self, start, end):

        res = self.range(start, end)

        while res is None:
            print('Search range failure. Sleeping 300 seconds.')
            time.sleep(300)
            res = self.range(start, end)

        print('length', len(res))
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            #current_keywords = self.getkws()
            curreid = db.get(_KEY_EVENT_PREFIX+ 'nextId')

            print(curreid)
            kwls = []
            # i = int(curreid)-3
            for i in range(int(curreid)-20,int(curreid)+1):
                try:
                    idcontent = db.get(_KEY_EVENT_PREFIX + str(i))
                    dic = json.loads(idcontent.decode('utf-8'))
                    kwls = kwls + (dic['info']['words'])
                except:
                    print("exception")

            kwls = list(set(kwls))

            print(start,end)
            expiry = start - self.delta * 1200

            for word in kwls:
                count = 0
                keystr= _KEY_EVENT_KEYWORDS_TRACK2+ ':' + word
                #print keystr
                for row in res:
                    txt = row[0]
                    #print txt
                    if txt.find(word)>-1:
                        count += 1
                if count>0:
                    print(word,count)

                db.hset(keystr, start,count)
                expired = db.hexists(keystr,expiry)
                if (expired):
                    db.hdel(keystr,expiry)

        except:
            print('connection failure.')
            print('Search range failure. Sleeping 30 seconds.')
            time.sleep(30)
            db = redis.StrictRedis('10.0.109.33', port=8181)
            #current_keywords = self.getkws()
            curreid = db.get(_KEY_EVENT_PREFIX+ 'nextId')

            print(curreid)
            kwls = []
            # i = int(curreid)-3
            for i in range(int(curreid)-20,int(curreid)+1):
                try:
                    idcontent = db.get(_KEY_EVENT_PREFIX + str(i))
                    dic = json.loads(idcontent.decode('utf-8'))
                    kwls = kwls + (dic['info']['words'])
                except:
                    print("exception")

            kwls = list(set(kwls))

            print(start,end)
            expiry = start - self.delta * 1200

            for word in kwls:
                count = 0
                keystr= _KEY_EVENT_KEYWORDS_TRACK2+ ':' + word
                #print keystr
                for row in res:
                    txt = row[0]
                    #print txt
                    if txt.find(word)>-1:
                        count += 1
                if count>0:
                    print(word,count)

                db.hset(keystr, start,count)
                expired = db.hexists(keystr,expiry)
                if (expired):
                    db.hdel(keystr,expiry)
        print('LOADING FINISHED.', len(self.deq), start, end)

        self.start = end




    def next(self):
        if len(self.deq) == 0:

            if self.end:
                if self.start >= self.end:
                    return stream.End_Of_Stream
            else:
                while self.start >= datetime.now() - self.lag - self.delta:
                    print(self.start, datetime.now(), 'sleep 1 min.')
                    time.sleep(60)

            if len(self.deq) == 0:
                # try:
                self.load(self.start, self.start + self.delta)
                # except:
                #     print('Loading error!')

        if len(self.deq) == 0:
            return None

        item = self.deq.popleft()

        return item



def test():
    s = datetime(2017,6,6,7,38,0)
    e = None
    crawler = Crawler(s, e)

    while True:
        item = crawler.next()
        if item is stream.End_Of_Stream:
            break




if __name__ == "__main__":
    test()



