__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import numpy as np
from topic_sketch import topic_sketch as ts, preprocessor
from topic_sketch import stream as ts_stream
from experiment import tweet_stream3, detection
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def main():
    s = datetime.datetime(2016,11,1,0,0,0)
    e = None
    stream = tweet_stream3.TweetStreamFromDB(s, e)

    _preprocessor = preprocessor.Preprocessor(stream)

    detection_component = detection.DetectionComponent(_preprocessor)

    sketch = ts.TopicSketch()

    count = 0
    while True:

        result = detection_component.next()

        '''
        if np.random.random() < 0.001:
            count += 1
            print 'Processing ' + str(count) + 'K'
            '''

        if result is ts_stream.End_Of_Stream:
            return ts_stream.End_Of_Stream

        if result is None:
            continue

        ptweet, sig, keywords = result

        if np.random.random() < 0.001:
            count += 1
            print 'Processing ' + str(count) + 'K\t' + str(ptweet.datetime())

        #sketch.process(ptweet)

        #sketch.run_time_infer()



def process_log():
    events = dict()
    sigs = dict()
    ts = dict()

    import codecs
    output = codecs.open('./log_output.txt', 'w', 'utf-8')
    for line in codecs.open('./log.txt', 'r', 'utf-8'):
        if line.startswith('put '):
            line = line[4:]
            terms = line.split('\t')
            eid = int(terms[0])
            events[eid] = line[len(terms[0]):]
        if line.startswith('detail'):
            obj = eval(line[7:])
            sig = obj['info']['significance']
            sigs[eid] = sig
            ts[eid] = obj['info']['dtime']

    for eid in events:
        output.write(str(eid) + '\t' + str(sigs[eid]) + '\t' + ts[eid] + '\t' + events[eid] + '\n')


from experiment import tweet_user
if __name__ == "__main__":
    main()
    #####################################################
    #print tweet_user.get_user_icon('1249193625')
    #print tweet_user.get_user_icon('1000000962')
    #print tweet_user.get_user_icon('3044210254')
    #print tweet_user.get_user_icon('1234567890')
