__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'



import time
import datetime


class NumberItem:

    def __init__(self, _t, _number):
        if isinstance(_t, datetime.datetime):
            self.timestamp = time.mktime(_t.timetuple())
        else:
            self.timestamp = _t

        self.number = _number

    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

class StringItem:

    def __init__(self, _t, _str):
        if isinstance(_t, datetime.datetime):
            self.timestamp = time.mktime(_t.timetuple())
        else:
            self.timestamp = _t

        self.str = _str

    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

class RawTweetItem:

    def __init__(self, _t, _uid, _str):
        if isinstance(_t, datetime.datetime):
            self.timestamp = time.mktime(_t.timetuple())
        else:
            self.timestamp = _t

        self.str = _str
        self.uid = _uid

        self.retweet_flag = False

        self.attached_obj = None

    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

    def attach(self, obj):
        self.attached_obj = obj

    def is_retweet(self):
        if self.attached_obj:
            return self.attached_obj["source_mid"] is not None

        return None

    def who_is_retweeted(self):
        if self.attached_obj:
            source_uid = self.attached_obj["source_uid"]
            if source_uid:
                return source_uid

        return None


class PreprocessedTweetItem:

    def __init__(self, _t, _uid, _tokens, _original_tweet):
        if isinstance(_t, datetime.datetime):
            self.timestamp = time.mktime(_t.timetuple())
        else:
            self.timestamp = _t

        self.tokens = _tokens
        self.uid = _uid

        self.original_tweet = _original_tweet

    def datetime(self):
        return datetime.datetime.fromtimestamp(self.timestamp)

    def is_retweet(self):
        return self.original_tweet.is_retweet()


class EndOfStream:

    def __init__(self):
        pass


End_Of_Stream = EndOfStream()

class ItemStream:

    def next(self):
        pass

class ItemStreamFromList(ItemStream):

    def __init__(self, _list):
        self.index = -1;
        self.list = _list

    def next(self):
        self.index += 1
        if self.index < len(self.list) :
            return self.list[self.index]
        return None

    def reset(self):
        self.index = -1;