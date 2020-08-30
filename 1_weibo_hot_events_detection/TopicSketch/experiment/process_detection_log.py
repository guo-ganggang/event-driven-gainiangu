__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import datetime
import exp_config
from datetime import datetime as date


_THREAD_GAP = eval(exp_config.get('process_detection_log', 'thread_gap'))

def terms_to_values(terms):
    _t = datetime.datetime.strptime(terms[0], '%Y-%m-%d %H:%M:%S')
    _count = float(terms[1])
    _ewma = float(terms[2])
    _ewmvar = float(terms[3])
    _sig = float(terms[4])
    _keywords = terms[5]
    return _t, _count, _ewma, _ewmvar, _sig, _keywords

class Slice:

    def __init__(self):
        self.start = 0.0
        self.end = 0.0
        self.keywords = None
        self.sig = 0.0
        self.first_sig = 0.0
        self.thread = []
        self.first_keywords = None


    def new_thread(self, terms):
        _t, _count, _ewma, _ewmvar, _sig, _keywords = terms_to_values(terms)
        self.start = _t
        self.end = _t
        self.keywords = set(_keywords.split(','))
        self.thread.append(terms)
        self.first_sig = _sig
        self.sig = _sig
        self.first_keywords = _keywords

    def add_to_thread(self, terms):
        _t, _count, _ewma, _ewmvar, _sig, _keywords = terms_to_values(terms)

        kw1, kw2 = _keywords.split(',')

        if _t - self.end <= datetime.timedelta(minutes=1):
            if kw1 not in self.keywords and kw2 not in self.keywords: #!!!
                return False
        elif kw1 not in self.keywords or kw2 not in self.keywords: #!!!
            return False

        if _t - self.end > datetime.timedelta(minutes=_THREAD_GAP):
            return False

        if _sig > self.sig:
            self.sig = _sig

        self.end = _t
        self.thread.append(terms)
        self.keywords.add(kw1)
        self.keywords.add(kw2)

        return True


def process():
    ###
    _start_y = int(exp_config.get('process_detection_log', 'start_y'))
    _start_m = int(exp_config.get('process_detection_log', 'start_m'))
    _start_d = int(exp_config.get('process_detection_log', 'start_d'))

    _end_y = int(exp_config.get('process_detection_log', 'end_y'))
    _end_m = int(exp_config.get('process_detection_log', 'end_m'))
    _end_d = int(exp_config.get('process_detection_log', 'end_d'))

    _start_t = date(_start_y, _start_m, _start_d)
    _end_t = date(_end_y, _end_m, _end_d)

    _threshold = eval(exp_config.get('process_detection_log', 'signi_threshold'))

    ###

    threads = []

    _f = open(exp_config.get('process_detection_log', 'log_file'), 'r')  #!!!

    for line in _f:
        if not line.startswith('201'):
            continue

        line = line.rstrip('\n')

        terms = line.split('\t')
        _t, _count, _ewma, _ewmvar, _sig, _keywords = terms_to_values(terms)

        if _t < _start_t or _t > _end_t:
            continue

        if _sig < _threshold:
            continue

        create_new = True



        for thread in threads:
            if thread.add_to_thread(terms):
                create_new = False
                break

        if create_new:
            thread = Slice()
            thread.new_thread(terms)

            threads.append(thread)

    _f.close()

    #threads.sort(key = lambda x: x.sig, reverse = True)
    threads.sort(key = lambda x: x.start)

    _s = set() # for debugging

    count = 0
    for thread in threads:
        print  thread.start, thread.end, thread.sig, thread.keywords
        '''
        print '\hline'
        topic = ''
        for word in thread.keywords:
            topic = topic + word + ', '
        print thread.start.strftime('%Y-%m-%d') + '&' + topic + '&\\\\'

        count += 1

        _s.add(thread.start.strftime('%Y-%m-%d'))

        #print count, len(_s)

        if count == 50:
            break
        '''
    return threads

    #return threads[:50]


def get_top_sig():
    terms = []

    _f = open(exp_config.get('process_detection_log', 'log_file'), 'r')  #!!!

    for line in _f:
        if not line.startswith('201'):
            continue

        line = line.rstrip('\n')

        term = line.split('\t')

        terms.append(term)

    terms.sort(key = lambda x: terms_to_values(x)[4], reverse=True)

    for term in terms:
        _t, _count, _ewma, _ewmvar, _sig, _keywords = terms_to_values(term)
        print _t, _count, _ewma, _ewmvar, _sig, _keywords



def main():

    #get_top_sig()
    process()



if __name__ == "__main__":
    main()
