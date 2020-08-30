__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

from datetime import datetime, date, timedelta as td

import MySQLdb

import topic_sketch.stream as stream

import exp_config


def source2tweet(source):
    _t = source["created_at"]#datetime.strptime(source["created_at"], '%Y-%m-%d %H:%M')
    _user = source["uid"]
    _tweet = source["text"]

    item = stream.RawTweetItem(_t, _user, _tweet)
    item.attach(source)
    return item

class TweetStreamFromDB(stream.ItemStream):

    def __init__(self):
        _start_y = int(exp_config.get('stream', 'start_y'))
        _start_m = int(exp_config.get('stream', 'start_m'))
        _start_d = int(exp_config.get('stream', 'start_d'))

        _end_y = int(exp_config.get('stream', 'end_y'))
        _end_m = int(exp_config.get('stream', 'end_m'))
        _end_d = int(exp_config.get('stream', 'end_d'))

        self.dy_start = date(_start_y, _start_m, _start_d)
        self.dy_end = date(_end_y,_end_m,_end_d)

        self.connection = MySQLdb.connect(host='?', user='?', db='?', charset='utf8')

        cursor = self.connection.cursor()
        cursor.execute("desc weibo_timelines")
        id = 0
        self.id_map = {}
        for column in cursor.fetchall():
            self.id_map[column[0]] = id
            id += 1

        self.cursor = self.connection.cursor()

        _time0 = self.dy_start.strftime("%Y-%m-%d")
        _time1 = (self.dy_start + td(days=1)).strftime("%Y-%m-%d")

        sql_str = 'select * from ' + 'weibo_timelines' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
        print sql_str

        self.cursor.execute(sql_str)




    def next(self):
        row = self.cursor.fetchone()

        if row is None:
            self.cursor.close()
            self.connection.close()

            self.dy_start = self.dy_start + td(days=1)
            if self.dy_start < self.dy_end:
                self.connection = MySQLdb.connect(host='?', user='?', db='?', charset='utf8')

                self.cursor = self.connection.cursor()

                _time0 = self.dy_start.strftime("%Y-%m-%d")
                _time1 = (self.dy_start + td(days=1)).strftime("%Y-%m-%d")

                sql_str = 'select * from ' + 'weibo_timelines' + ' where created_at >= "%s" and created_at < "%s" order by created_at' % (_time0, _time1)
                print sql_str

                self.cursor.execute(sql_str)

                row = self.cursor.fetchone()
            else:
                return stream.End_Of_Stream

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
        return item


import jieba
import codecs
from topic_sketch import stop_words
def test():
    f = codecs.open('./output.txt', 'w', 'utf-8')
    tweet_stream = TweetStreamFromDB()

    counts = {}

    while(True):

        twt = tweet_stream.next()
        if twt is stream.End_Of_Stream:
            break

        try:
            f.write(twt.str)
            print twt.str
            f.write('\n')
        except:
            break

        for token in jieba.cut(twt.str):

            #if stop_words.contains(token):
            #    continue

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


