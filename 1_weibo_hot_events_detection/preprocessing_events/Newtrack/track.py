__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import time

from datetime import datetime, date, timedelta as td

import MySQLdb, redis

import topic_sketch.stream as stream

from collections import deque

from timeout import timeout

import exp_config

import twokenize


_KEY_EVENT_CHANNEL = 'channel path'
_KEY_EVENT_PREFIX = _KEY_EVENT_CHANNEL + ':'
_KEY_EVENT_KEYWORDS = _KEY_EVENT_PREFIX + 'keywords'
_KEY_EVENT_KEYWORDS_TRACK2 = _KEY_EVENT_PREFIX + 'track2'

class Crawler:

    def __init__(self, start, end):
        self.deq = deque([])

        self.start = start

        self.end = end

        self.delta = td(seconds=30)

        self.lag = td(minutes=2*60 + 30)

        self.host = 'X.X.X.X'
        self.user = 'user'
        self.db = 'db'
        self.charset = 'utf8'

        self.connection = MySQLdb.connect(host=self.host, user=self.user, db=self.db, charset=self.charset, passwd='password')
        cursor = self.connection.cursor()
        cursor.execute("desc timelines2")
        id = 0
        self.id_map = {}
        for column in cursor.fetchall():
            self.id_map[column[0]] = id
            id += 1
        cursor.close()

    @timeout(60*10)
    def range(self, t_start, t_end):
        try:

            print 'closing old connection...'
            self.connection.close()
            print 'sleep 2 seconds'
            time.sleep(2)
            print 'trying to reconnect db ...'
            self.connection = MySQLdb.connect(host=self.host, user=self.user, db=self.db, charset=self.charset, passwd='password')
            print 'successful connection!'
            cursor = self.connection.cursor()

            _time0 = t_start.strftime("%Y-%m-%d %H:%M:%S")
            _time1 = t_end.strftime("%Y-%m-%d %H:%M:%S")

            sql_str = 'select text, created_at from ' + 'timelines2' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
            print sql_str

            cursor.execute(sql_str)
            ret = cursor.fetchall()
            cursor.close()

        except:
            print 'something wrong in DB.'
            return None

        return ret

    def load(self, start, end):

        res = self.range(start, end)

        while res is None:
            print 'Search range failure. Sleeping 300 seconds.'
            time.sleep(300)
            res = self.range(start, end)

        print 'length', len(res)
        try:
            db = redis.StrictRedis('X.X.X.X', port=8181)
            current_keywords = db.lrange(_KEY_EVENT_KEYWORDS, 0, -1)
            if current_keywords:
                current_keywords = set(map(lambda x: x.decode('utf-8'), current_keywords))
            else:
                current_keywords = set()
            #print 'current_keywords', current_keywords
            for row in res:
                txt = row[0]
                t = row[1]
                tokens = twokenize.tokenizeRawTweetText(txt)
                for token in set(tokens):
                    #print token
                    if token in current_keywords:
                        #print 'hit!', token
                        db.rpush(_KEY_EVENT_KEYWORDS_TRACK + ':' + token, t)
                self.deq.append(1)

        except:
            print 'connection failure.'

        print 'LOADING FINISHED.', len(self.deq), start, end

        self.start = end

    def next(self):
        if len(self.deq) == 0:

            if self.end:
                if self.start >= self.end:
                    return stream.End_Of_Stream
            else:
                while self.start >= datetime.now() - self.lag - self.delta:
                    print self.start, datetime.now(), 'sleep 1 min.'
                    time.sleep(60)

            if len(self.deq) == 0:
                try:
                    self.load(self.start, self.start + self.delta)
                except:
                    print 'Loading error!'

        if len(self.deq) == 0:
            return None

        item = self.deq.popleft()

        return item



def test():
    s = datetime(2016,11,20,19,30,0)
    e = None
    crawler = Crawler(s, e)

    while True:
        item = crawler.next()
        if item is stream.End_Of_Stream:
            break




if __name__ == "__main__":
    test()



