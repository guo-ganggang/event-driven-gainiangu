__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import codecs
_stop_words = set([line.strip() for line in codecs.open('./weibo-stopwords.txt', 'r', 'utf-8')])
_stop_words = _stop_words.union(set([line.strip() for line in codecs.open('./twitter-stopwords.txt', 'r', 'utf-8')]))


def contains(word):
    return word in _stop_words
