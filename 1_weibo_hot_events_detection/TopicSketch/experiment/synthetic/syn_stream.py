__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import numpy as np

from topic_sketch import stream as stream

import poisson

import hpk


_N_words = 10

class SynTweetStream(stream.ItemStream):

    def __init__(self):
        (sq1, rate1) = poisson.simulate(period=600)
        sq1 = np.array(sq1)

        (sq2, rate2) = hpk.simulate(180)
        sq2 = np.array(sq2) + 420

        self.create_parameters()

        t0 = 1425847547.

        stream1 = []
        for element in sq1:
            item = stream.RawTweetItem(t0 + 60*element, 0, self.get_doc(self.g_topics))
            stream1.append(item)

        stream2 = []
        for element in sq2:
            item = stream.RawTweetItem(t0 + 60*element, 0, self.get_doc(self.b_topics))
            stream2.append(item)

        self.stream_all = stream1 + stream2

        self.stream_all.sort(key=lambda x: x.datetime())

        self.index = 0

        # debugging
        #print len(self.stream_all)

    @staticmethod
    def get_doc_len():
        return 50#np.random.poisson(50)

    def get_doc(self, topic):
        doc = ''

        l = self.get_doc_len()
        word_counts = np.random.multinomial(l, topic)

        for w in xrange(_N_words):
            word_count = word_counts[w]

            for i in xrange(word_count):
                doc += (str(w) + ' ')

        return doc

    def create_parameters(self):
        # for bursty topics
        self.b_topics = np.array([0.0, 0.0, 0.1, 0.6, 0.2, 0.1, 0, 0, 0, 0])

        # for general topics
        self.g_topics = np.array([0.4, 0.3, 0.2, 0.1, 0, 0, 0, 0, 0, 0])

    def next(self):
        if self.index < len(self.stream_all):
            ret = self.stream_all[self.index]
            self.index += 1

            #print ret.datetime(), ret.str
            return ret

        return stream.End_Of_Stream
