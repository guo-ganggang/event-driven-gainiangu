__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import copy

from collections import deque

import topic_sketch.stream as stream

from topic_sketch import preprocessor

import datetime



class TweetStreamFromFile(stream.ItemStream):

    def __init__(self):
        self.deq = deque([])
        f = open('./tweets.txt', 'r')

        _t = None
        _user = None
        _tweet = None

        for line in f:
            if line.startswith('content: '):
                _tweet = line.split('content: ')[1]

            if line.startswith('userId: '):
                _user = eval(line.split('userId: ')[1])

            if line.startswith('publishedTimeGmt: '):
                _t = eval(line.split('publishedTimeGmt: ')[1]) / 1000
                _t += 8*60*60# 8 hours

            if line.startswith('-------------'):
                item = stream.RawTweetItem(_t, _user, _tweet)
                self.deq.append(item)

        print 'LOADING FINISHED.'

    def next(self):
        if len(self.deq) == 0:
            return stream.End_Of_Stream

        item = self.deq.pop()

        '''
        if item.datetime() > datetime.datetime(2015, 7, 7, 12, 0, 0):
            return stream.End_Of_Stream'''

        return item

def test():
    tweet_stream = TweetStreamFromFile()
    _preprocessor = preprocessor.Preprocessor(tweet_stream)

    tweet = _preprocessor.next()

    while tweet is not stream.End_Of_Stream:
        if tweet is None:
            tweet = _preprocessor.next()
            continue

        tokens = tweet.tokens
        t = tweet.datetime()

        if '#mh370' in tokens or 'mh370' in tokens:
            print t, tokens

        tweet = _preprocessor.next()


#test()

