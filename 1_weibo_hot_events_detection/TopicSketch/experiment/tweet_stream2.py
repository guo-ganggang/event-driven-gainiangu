__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import time

from datetime import datetime, date, timedelta as td

import MySQLdb

import topic_sketch.stream as stream

from collections import deque

from timeout import timeout

import sys_monitor

import exp_config


def source2tweet(source):
    _t = datetime.strptime(source["created_at"], '%Y-%m-%d %H:%M')
    _user = source["uid"]
    _tweet = source["text"]

    item = stream.RawTweetItem(_t, _user, _tweet)
    item.attach(source)
    return item

class TweetStreamFromDB(stream.ItemStream):

    def __init__(self, start, end):
        self.deq = deque([])

        self.start = start

        self.end = end

        self.delta = td(minutes=120)

        self.lag = td(minutes=60)

        self.host = exp_config.get('database', 'host')
        self.user = exp_config.get('database', 'user')
        self.db = exp_config.get('database', 'db')
        self.charset = exp_config.get('database', 'charset')

        self.connection = MySQLdb.connect(host=self.host, user=self.user, db=self.db, charset=self.charset)
        cursor = self.connection.cursor()
        cursor.execute("desc weibo_timelines")
        id = 0
        self.id_map = {}
        for column in cursor.fetchall():
            self.id_map[column[0]] = id
            id += 1
        cursor.close()

    @timeout(60*10)
    def range(self, t_start, t_end):
        try:
            try:
                cursor = self.connection.cursor()
            except:
                print 'closing old connection...'
                self.connection.close()
                print 'trying to reconnect db ...'
                self.connection = MySQLdb.connect(host=self.host, user=self.user, db=self.db, charset=self.charset)
                print 'successful connection!'
                cursor = self.connection.cursor()

            _time0 = t_start.strftime("%Y-%m-%d %H:%M:%S")
            _time1 = t_end.strftime("%Y-%m-%d %H:%M:%S")

            sql_str = 'select * from ' + 'weibo_timelines' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
            print sql_str

            cursor.execute(sql_str)
            ret = cursor.fetchall()
            cursor.close()

        except:

            return None

        return ret

    def load(self, start, end):

        res = self.range(start, end)

        while res is None:
            print 'Search range failure. Sleeping 300 seconds.'
            time.sleep(300)
            res = self.range(start, end)

        for row in res:
            _obj = {
                "mid" : row[self.id_map["mid"]],
                "uid" : row[self.id_map["uid"]],
                "retweet_num" : row[self.id_map["retweet_num"]],
                "comment_num" : row[self.id_map["comment_num"]],
                "favourite_num" : row[self.id_map["favourite_num"]],
                "created_at" : row[self.id_map["created_at"]],
                "from" : row[self.id_map["from"]],
                "text" : row[self.id_map["text"]],
                "entity" : row[self.id_map["entity"]],
                "source_mid" : row[self.id_map["source_mid"]],
                "source_uid" : row[self.id_map["source_uid"]],
                "mentions" : row[self.id_map["mentions"]],
                "check_in" : row[self.id_map["check_in"]],
                "check_in_url" : row[self.id_map["check_in_url"]],
                "is_deleted" : row[self.id_map["is_deleted"]],
                "timestamp" : row[self.id_map["timestamp"]],
            }

            _t = datetime.strptime(_obj["created_at"], '%Y-%m-%d %H:%M')
            _user = _obj["uid"]
            _tweet = _obj["text"]

            item = stream.RawTweetItem(_t, _user, _tweet)
            item.attach(_obj)

            self.deq.append(item)

        print 'LOADING FINISHED.', len(self.deq), start, end
        dt = self.delta.seconds / 60.0
        sys_monitor.report_rate(len(self.deq)/dt, end)

        self.start = end

    def next(self):
        if len(self.deq) == 0:

            if self.end:
                if self.start >= self.end:
                    return stream.End_Of_Stream
            else:
                while self.start >= datetime.now() - self.lag - self.delta:
                    time.sleep(60)

            while len(self.deq) == 0:
                self.load(self.start, self.start + self.delta)

        item = self.deq.popleft()

        return item


import jieba
import codecs
from topic_sketch import stop_words
def test():
    s = datetime(2015,12,7,0,0,0)
    e = datetime(2015,12,8,0,0,0)
    f = codecs.open('./output.txt', 'w', 'utf-8')
    tweet_stream = TweetStreamFromDB(s, e)

    counts = {}

    while(True):

        twt = tweet_stream.next()
        if twt is stream.End_Of_Stream:
            break
        for token in jieba.cut(twt.str):

            if stop_words.contains(token):
                continue

            if token in counts:
                counts[token] += 1
            else:
                counts[token] = 1


    ks = counts.keys()

    ks.sort(key=lambda x:counts[x], reverse=True)

    for k in ks[:10000]:
        f.write(k + '\n')




if __name__ == "__main__":
    test()


