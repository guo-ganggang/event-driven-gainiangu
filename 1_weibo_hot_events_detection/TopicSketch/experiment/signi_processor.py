__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import topic_sketch.stemmer as stemmer
import fast_signi


import exp_config


_SIGNI_THRESHOLD = eval(exp_config.get('detection', 'signi_threshold'))


class SparseSigniContainer():
    _THRESHOLD_FOR_CLEANING = eval(exp_config.get('detection', 'threshold_for_cleaning'))
    _CAPACITY_FOR_CLEANING = eval(exp_config.get('detection', 'capacity_for_cleaning'))


    def __init__(self):
        self.container = {}

    def _clean(self, _timestamp):
        to_be_cleaned_up = []
        for key, value in self.container.iteritems():
            value.observe(_timestamp, 0.)
            if value.ewma <= self._THRESHOLD_FOR_CLEANING:
                to_be_cleaned_up.append(key)

        print 'cleaning', len(to_be_cleaned_up), 'items...'
        for key in to_be_cleaned_up:
            self.container.pop(key)

    def get(self, _id, _timestamp):
        # check for cleaning
        if len(self.container) > self._CAPACITY_FOR_CLEANING:
            self._clean(_timestamp)

        # return
        if _id in self.container:
            return self.container[_id]
        else:
            sig_scorer = fast_signi.SignificanceScorer()

            self.container[_id] = sig_scorer
            return sig_scorer





class SigProcessor:

    def __init__(self):
        self.sig_scorers = SparseSigniContainer()

    def process(self, _ptweet):

        self.timestamp = _ptweet.timestamp
        tokens = _ptweet.tokens

        # stemming
        tokens = map(lambda x: stemmer.stem(x), tokens)

        if len(tokens) < 3:
            return None

        set_of_tokens = set()
        for token in tokens:
            set_of_tokens.add(token)

        result_list = list()

        for token1 in set_of_tokens:
            for token2 in set_of_tokens:
                if ',' in token1 or ',' in token2:
                    continue

                if token1 >= token2:
                    continue
                list_of_tokens = [token1, token2]
                list_of_tokens.sort()
                token = list_of_tokens[0] + ',' + list_of_tokens[1]
                count, ewma, ewmavar, sig = self.sig_scorers.get(token, self.timestamp).observe(self.timestamp, 1.0)
                if sig > _SIGNI_THRESHOLD:
                    result_list.append((count, ewma, ewmavar, sig, token))

        if len(result_list) > 0:
            tokens = set()
            for result in result_list:
                token = result[4]
                kws = token.split(',')
                for kw in kws:
                    tokens.add(kw)

            m_sig = max(map(lambda x: x[3], result_list))

            #print 'SIG', m_sig, '#' + '#'.join(tokens) + '#' #!!! do not display

            return _ptweet.datetime(), 0, 0, 0, m_sig, tokens, _ptweet

        return None


















