__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import numpy
import datetime
import gzip
import cPickle as cpickle
import topic_sketch.fast_hashing as hashing
import matplotlib.pyplot as plt
import numpy as np
import experiment.exp_config as config


_SKETCH_BUCKET_SIZE = eval(config.get('sketch', 'sketch_bucket_size'))

def pairs(mat, words):
    shape = mat.shape
    n = shape[1]

    for w1 in words:
        for w2 in words:

            hashcode = numpy.array(hashing.hash_code(w1)) % n
            h1 = hashcode[0]

            hashcode = numpy.array(hashing.hash_code(w2)) % n
            h2 = hashcode[0]

            if h1 > h2:
                continue

            v = mat[h1, h2]
            if v > 0.005:
               print (w1, w2, v)


import math
def collision_rate(n, N):

    p = 1 - math.exp(-n*(n-1.)/(2.*N))

    print p

    return p


def collision(mat, words):
    shape = mat.shape
    n = shape[1]

    counts = {}
    table = {}
    for i in xrange(_SKETCH_BUCKET_SIZE):
        counts[i] = 0
        table[i] = []

    for w in words:
        hashcode = numpy.array(hashing.hash_code(w)) % n

        id = hashcode[0]
        counts[id] += 1
        table[id].append(w)

    plt.plot(map(lambda x: counts[x], counts))
    plt.show()
    print table

from nltk.stem.lancaster import *
from nltk.stem.snowball import *
def stemming(words):

    stemmer = SnowballStemmer("english")

    print len(words)
    new_words = dict()

    for w in words:
        try:
            w_ = stemmer.stem(w)
        except:
            w_ = w

        if w_ in new_words:
            new_words[w_].append(w)
        else:
            new_words[w_] = [w]

    print len(new_words)

    for w in new_words:
        if len(new_words[w]) > 1:
            print w, new_words[w]

import topic_sketch.stemmer as stemmer
import topic_sketch.fast_hashing as fast_hashing
import topic_sketch.solver as solver
import matplotlib.pyplot as plt
import math

def remove_negative_terms(v):
    ret = np.zeros(_SKETCH_BUCKET_SIZE)
    for i in xrange(_SKETCH_BUCKET_SIZE):
        if v[i].real >= 0.001:
            ret[i] = v[i].real

    return ret / sum(ret)

def entropy(prob):
    ret = 0.0
    for i in xrange(len(prob)):
        if prob[i] > 0. :
            ret -= prob[i] * math.log(prob[i])

    return ret

def choose(candidates): # each candidate is K sets of words

    H = len(candidates)

    ret = np.zeros(H, dtype=int)

    max_similarity = 0.0
    for k0 in xrange(len(candidates[0])):
        for k1 in xrange(len(candidates[1])):
            s0 = candidates[0][k0]
            s1 = candidates[1][k1]

            if len(s0) == 0 or len(s1) == 0:
                continue

            #similarity = (len(s0.intersection(s1)) + 0.0) / len(s0.union(s1))
            similarity = len(s0.intersection(s1))
            if similarity > max_similarity:
                ret[0] = k0
                ret[1] = k1
                max_similarity = similarity

    s = candidates[0][ret[0]].intersection(candidates[1][ret[1]])

    print s # for debugging

    for h in xrange(2, H):
        max_similarity = 0.0
        for k in xrange(len(candidates[h])):
            sh = candidates[h][k]
            if len(sh) == 0:
                continue
            #similarity = (len(s.intersection(sh)) + 0.0) / len(s.union(sh))
            similarity = len(s.intersection(sh))
            if similarity > max_similarity:
                ret[h] = k
                max_similarity = similarity

    return ret

def ex2():

    _f = gzip.open('/Users/weixie/Downloads/topicsketch_old/topicsketch_cut/20140120_12_33_22', 'rb')
    sketch_status = cpickle.load(_f)
    _f.close()

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]


    '''
    plt.matshow(numpy.absolute(m.toarray()[2400:2500, 2400:2500]), fignum=None, cmap=plt.cm.gray)
    plt.colorbar()
    plt.show()
    '''
    '''
    for h in xrange(5):
        a, r, v = solver.solve(_m2[h], _m3[h], _SKETCH_BUCKET_SIZE, 5)

        print sorted(a, key=lambda x: np.abs(x))



    #infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, 5), range(fast_hashing.HASH_NUMBER))
    '''
    h = 0
    K = 10

    mat = _m2[h]

    x = []
    for i in xrange(_SKETCH_BUCKET_SIZE):
        x.append(mat[i,i])

    plt.plot(x)
    plt.show()


    index = np.argmax(np.array(x))

    print index

    for _w in _words:
        w = stemmer.stem(_w)
        if hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE == index:
            print _w


    '''
    for y in sorted(x):
        print x.index(y), y
    '''


    a, r, v = solver.solve(_m2[h], _m3[h], _SKETCH_BUCKET_SIZE, K)
    print a
    print r

    print v[index,:]

    sorted_a = sorted(a, reverse=True)


    #k = a.index(max(a, key=lambda x: x.real))

    for _k in xrange(K):
        k = a.index(sorted_a[_k])


        prob = v[:,k]

        prob = remove_negative_terms(prob)








        print k, sorted_a[_k]
        print 'entropy', k, entropy(prob)

        plt.plot(prob)
        plt.show()

        for _w in _words:
            w = stemmer.stem(_w)
            p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
            if p > 0.025:
                print _w, p

        print '########################################'



import time
def ex3():
    _f = gzip.open('/Users/weixie/Downloads/topicsketch_old/topicsketch_cut/20140128_21_52_28', 'rb')
    sketch_status = cpickle.load(_f)
    _f.close()

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]

    H = 5
    K = 10

    t = time.time()
    infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, K), range(fast_hashing.HASH_NUMBER))
    print 't0 = ' + str(time.time() - t)

    t = time.time()
    candidates = []
    for h in xrange(H):
        a, r, v = infer_results[h]
        candidate = []
        for k in xrange(K):
            s = set()

            prob = v[:,k]

            prob = remove_negative_terms(prob)

            # filtering
            if a[k].real < 1.0:
                continue
            if entropy(prob) > 6.0:
                continue

            for _w in _words:
                w = stemmer.stem(_w)
                p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
                if p > 0.01:
                    s.add(_w)

            candidate.append(s)

        candidates.append(candidate)

    for h in xrange(H):
        print '------------------------------'
        for k in xrange(len(candidates[h])):
            print candidates[h][k]
        print '------------------------------'


    index = choose(candidates)

    for h in xrange(H):
        print candidates[h][index[h]]

    topic_words = candidates[0][index[0]]

    for h in xrange(1,H):
        topic_words = topic_words.intersection(candidates[h][index[h]])

    output = ''
    for w in topic_words:
        output = output + w + ','

    print output

    print 't1 = ' + str(time.time() - t)


def ex4():
    _f = gzip.open('/Users/weixie/Downloads/topicsketch_old/topicsketch_cut/20140128_21_52_28', 'rb')
    sketch_status = cpickle.load(_f)
    _f.close()

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]

    H = 5
    K = 50

    t = time.time()
    infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, K), range(fast_hashing.HASH_NUMBER))
    print 't0 = ' + str(time.time() - t)

    t = time.time()
    candidates = []
    for h in xrange(H):
        a, r, v = infer_results[h]
        candidate = []
        for k in xrange(K):
            s = set()

            prob = v[:,k]

            prob = remove_negative_terms(prob)


            # filtering
            if a[k].real < 1.0:
                continue
            if entropy(prob) > 6.0:
                continue


            for _w in _words:
                w = stemmer.stem(_w)
                p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
                if p > 0.01:
                    s.add(_w)

            candidate.append(s)

        candidates.append(candidate)

    for h in xrange(H):
        print '------------------------------'
        for k in xrange(len(candidates[h])):
            print candidates[h][k]
        print '------------------------------'

    topic_words = candidates[0][-1]

    for h in xrange(1,H):
        topic_words = topic_words.union(candidates[h][-1])

    output = ''
    for w in topic_words:
        support = 0
        for h in xrange(H):
            if w in candidates[h][-1]:
                support += 1
        if support >= H - 1:
            output = output + w + ','

    print output

    print 't1 = ' + str(time.time() - t)


def simi(d1, d2):
    ret = 0.0
    for k1, v1 in d1.iteritems():
        if k1 in d2:
            ret += v1 * d2[k1]

    return ret



def ex5():
    _f = gzip.open('/Users/weixie/Downloads/topicsketch_old/topicsketch_cut/20140120_12_33_22', 'rb')
    sketch_status = cpickle.load(_f)
    _f.close()

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]



    #######################
    mat = _m2[0]
    x = []  # for debugging
    for i in xrange(_SKETCH_BUCKET_SIZE):
        x.append(mat[i,i])

    id = np.argmax(np.array(x))
    for _w in _words:
        w = stemmer.stem(_w)
        if hashing.hash_code(w)[0] % _SKETCH_BUCKET_SIZE == id:
            print _w
    #######################

    H = 5
    K = 10

    t = time.time()
    infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, K), range(fast_hashing.HASH_NUMBER))
    print 't0 = ' + str(time.time() - t)

    t = time.time()
    candidates = []
    more_candidates = []
    for h in xrange(H):
        a, r, v = infer_results[h]
        candidate = []
        more_candidate = []
        for k in xrange(K):
            s = set()
            more_s = set()

            prob = v[:,k]

            prob = remove_negative_terms(prob)

            # filtering
            if a[k].real < 1.0:
                continue
            if entropy(prob) > 6.0:
                continue

            for _w in _words:
                w = stemmer.stem(_w)
                p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
                if p >= 0.025:
                    s.add(_w)
                if p >= 0.015:
                    more_s.add(_w)

            candidate.append(s)
            more_candidate.append(more_s)

        candidates.append(candidate)
        more_candidates.append(more_candidate)

    for h in xrange(H):
        print '------------------------------'
        for k in xrange(len(candidates[h])):
            print candidates[h][k]
        print '------------------------------'


    index = choose(candidates)


    for h in xrange(H):
        a, r, v = infer_results[h]
        plt.plot(v[:,h].real)
        plt.show()

    for h in xrange(H):
        print candidates[h][index[h]]

    topic_words = more_candidates[0][index[0]]

    for h in xrange(1,H):
        topic_words = topic_words.intersection(more_candidates[h][index[h]])

    output = ''
    for w in topic_words:
        output = output + w + ','

    print output

    print 't1 = ' + str(time.time() - t)

def join(list_of_sets):
    if len(list_of_sets) == 0:
        return set()

    output = list_of_sets[0]

    for i in xrange(1, len(list_of_sets)):
        output = output.intersection(list_of_sets[i])

    return output


def recover(s, words):
    output = set()
    for word in words:
        if stemmer.stem(word) in s:
            if words[word] >= 5:#!!!
                output.add(word)

    return output


import topic_sketch.apriori as apriori


def connect_words(words):
    output = ''
    for w in words:
        try:
            str(w)
            output = output + w + ','
        except:
            continue

    return output

def hash_code(s, h):
    output = []
    for w in s:
        h_v = hashing.hash_code(stemmer.stem(w))[h] % _SKETCH_BUCKET_SIZE
        output.append(h_v)

    return output

def support_distance(support):
    return max(support.values()) - min(support.values())


def ex(_fstr):
    _f = gzip.open(_fstr, 'rb')
    sketch_status = cpickle.load(_f)
    _f.close()

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]



    #######################
    mat = _m2[0]
    x = []  # for debugging
    for i in xrange(_SKETCH_BUCKET_SIZE):
        x.append(mat[i,i])

    id = np.argmax(np.array(x))
    for _w in _words:
        w = stemmer.stem(_w)
        if hashing.hash_code(w)[0] % _SKETCH_BUCKET_SIZE == id:
            print _w
    #######################

    H = 5
    K = 15

    t = time.time()
    infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, K), range(fast_hashing.HASH_NUMBER))
    print 't0 = ' + str(time.time() - t)

    t = time.time()
    transactions = []
    topics_group = []
    for h in xrange(H):
        topics = dict()
        a, r, v = infer_results[h]
        for k in xrange(K):
            s = set()
            topic = set()
            prob = v[:,k]

            prob = remove_negative_terms(prob)

            # filtering
            if a[k].real < 1.0:
                continue
            if entropy(prob) > 6.0:
                continue

            for _w in _words:
                w = stemmer.stem(_w)
                p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
                if p >= 0.0250:
                    s.add(w)
                if p >= 0.0150:
                    topic.add(w)

            transactions.append(apriori.Transaction(s, h, k))
            topics[k] = topic

            print h, k, a[k].real, map(lambda w, h: (w,h), s, hash_code(s, h))# for debugging

        topics_group.append(topics)


    '''
    output = apriori.apriori(transactions, 3)
    for ws in output:
        print connect_words(recover(ws.words, _words)), np.median(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))
    print '-------------------------------'
    '''

    output = apriori.apriori(transactions, 4)
    for ws in output:
        print '['
        print ws.support, support_distance(ws.support)
        print connect_words(recover(ws.words, _words)), np.max(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))
        print connect_words(recover(join(map(lambda item: topics_group[item[0]][item[1]], ws.support.iteritems())), _words)), \
            np.max(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems()))), \
            np.median(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))
        print ']'
    print '-------------------------------'

    '''
    output = apriori.apriori(transactions, 5)
    for ws in output:
        print '['
        print connect_words(recover(ws.words, _words)), np.median(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))
        print connect_words(recover(join(map(lambda item: topics_group[item[0]][item[1]], ws.support.iteritems())), _words)), \
            np.median(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))
        print ']'

    print '-------------------------------'
    '''

    print 't1 = ' + str(time.time() - t)


import cPickle as cpk
def simplified_ex(_fstr, _sketch_status = None, direct = False):
    if _fstr:
        _f = gzip.open(_fstr, 'rb')
        sketch_status = cpickle.load(_f)
        _f.close()
    else:
       sketch_status = _sketch_status

    _t = datetime.datetime.utcfromtimestamp(sketch_status[0])
    _words = sketch_status[1]
    _m2 = sketch_status[2]
    _m3 = sketch_status[3]



    #######################
    mat = _m2[0]
    x = []  # for debugging
    for i in xrange(_SKETCH_BUCKET_SIZE):
        x.append(mat[i,i])

    id = np.argmax(np.array(x))
    for _w in _words:
        w = stemmer.stem(_w)
        if hashing.hash_code(w)[0] % _SKETCH_BUCKET_SIZE == id:
            print 'significant', _w
    #######################

    H = fast_hashing.HASH_NUMBER
    K = eval(config.get('sketch', 'num_topics'))#15

    infer_results = map(lambda _h : solver.solve(_m2[_h], _m3[_h], _SKETCH_BUCKET_SIZE, K), range(H))

    if direct:
        return infer_results

    ### debugging
    print 'Inference finished.'
    ############

    transactions = []
    topics_group = []
    for h in xrange(H):
        topics = dict()
        a, r, v = infer_results[h]
        a_max = max(np.array(a).real)
        print a_max
        for k in xrange(K):
            s = set()
            topic = set()
            prob = v[:,k]

            prob = remove_negative_terms(prob)

            # filtering
            if a[k].real < 0.1*a_max:#1.0:
                continue
            if entropy(prob) > 6.0:
                continue

            _ranks = dict()
            for _w in _words:
                w = stemmer.stem(_w)
                p = prob[hashing.hash_code(w)[h] % _SKETCH_BUCKET_SIZE]
                _ranks[w] = p
                if p >= 0.0100:
                    s.add(w)
                if p >= 0.0075:
                    topic.add(w)

            _tops = sorted(_ranks.keys(), key=lambda x: _ranks[x], reverse=True)
            _top_n = 15
            if len(s) > _top_n:
                transactions.append(apriori.Transaction(set(_tops[:_top_n]), h, k))
                #print _top_n
            else:
                transactions.append(apriori.Transaction(s, h, k))
                #print len(s)

            topics[k] = topic

            print h, k, a[k].real, map(lambda w, h: (w,h,_ranks[w]), s, hash_code(s, h))# for debugging

        topics_group.append(topics)


    ### debugging
    print 'starting apriori.'
    #############


    output = apriori.apriori(transactions, 4)
    _result = dict()
    _result['time'] = _t
    _result['topics'] = list()

    print _t
    for ws in output:
        '''
        if support_distance(ws.support) > 5:
            continue'''

        _result['topics'].append((connect_words(recover(ws.words, _words)), connect_words(recover(join(map(lambda item: topics_group[item[0]][item[1]], ws.support.iteritems())), _words)), \
            np.max(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems()))), \
            np.median(np.array(map(lambda item: infer_results[item[0]][0][item[1]].real, ws.support.iteritems())))))

    if _fstr:
        out_file = open('E:/experiment/results/' + _fstr.split('/')[-1], 'wb')
        cpk.dump(_result, out_file)
        out_file.close()
    else:
        return _result


import os
import exp_config
def process_sketch(_dir):
    for f in os.listdir(_dir):

        ### for debugging
        '''
        if str(f) != '20141024_00_27_33':
            print 'pass' + str(f)
            continue'''
        #################

        try:
            simplified_ex(_dir + f)

        except:
            print 'error: ' + str(_dir + f)

def get_results(_dir):
    results = list()

    for f in os.listdir(_dir):
        try:
            result = cpk.load(open((_dir + f), 'rb'))
            results.append(result)
        except:
            print 'error: ' + str(_dir + f)

    return results

def top_topic(result):
    topics = result['topics']
    a = map(lambda x: x[2], topics)
    mx = max(a)
    for topic in topics:
        if topic[2] == mx:
            return topic

def top_topic_from_topics(topics):
    a = map(lambda x: x[3], topics)
    mx = max(a)
    for topic in topics:
        if topic[3] == mx:
            return topic

import topic_sketch.stemmer as stemmer
def to_latex_table_old(time, sig, topic):
    max_count = 15

    output_string = ''
    output_string += '\hline\n'
    output_string += (str(time) + '&')
    output_string += (str(sig) + '&')
    key_words = set(map(lambda x: stemmer.stem(x), topic[0].split(',')))
    #key_words = topic[0].split(',')
    words = set(map(lambda x: stemmer.stem(x), topic[1].split(',')))
    #words = topic[1].split(',')

    count = 0;
    for word in key_words:
        if len(word) > 0:
            output_string += ('\\textbf{' + word + '},')
            count += 1
            if count >= max_count:
                break
    for word in words:
        if word not in key_words:
            if len(word) > 0:
                output_string += (word + ',')
                count += 1
                if count >= max_count:
                    break

    output_string = output_string[:-1] + '\\\\'
    return output_string.replace(',', ' ')

def to_latex_table(time, sig, topics):
    max_count = 15

    # filtering...
    topics = filter(lambda topic: len(set(map(lambda x: stemmer.stem(x), topic[0].split(',')))) > 2, topics)

    # sort
    topics = sorted(topics, key=lambda topic: topic[3], reverse=True)  #  median

    if len(topics) == 0:
        return None

    num_row = len(topics)

    output_string = ''
    output_string += '\cline{1-3}\n'
    output_string += ('\multirow{' + str(num_row) + '}{*}{' + str(time).split(' ')[0] + '}&')
    output_string += ('\multirow{' + str(num_row) + '}{*}{' + str(sig) + '}&')



    first_time = True

    for topic in topics:
        key_words = set(map(lambda x: stemmer.stem(x), topic[0].split(',')))
        #key_words = topic[0].split(',')

        if len(key_words) <= 2: # include ''
            continue

        #words = set(map(lambda x: stemmer.stem(x), topic[1].split(',')))
        words = topic[1].split(',')

        if not first_time:
            output_string += '\n\cline{3-3}\n'
            output_string += '&&'
        else:
            first_time = False

        count = 0;
        for word in key_words:
            if len(word) > 0:
                output_string += ('\\textbf{' + word + '},')
                count += 1
                if count >= max_count:
                    break
        for word in words:
            if word not in key_words:
                if len(word) > 0:
                    output_string += (word + ',')
                    count += 1
                    if count >= max_count:
                        break

        output_string = output_string[:-1] + '\\\\'

    return output_string.replace(',', ' ')


def to_latex_table_without_sig(time, sig, topics):
    max_count = 15

    # filtering...
    topics = filter(lambda topic: len(set(map(lambda x: stemmer.stem(x), topic[0].split(',')))) > 2, topics)

    # sort
    topics = sorted(topics, key=lambda topic: topic[3], reverse=True)  #  median

    if len(topics) == 0:
        return None

    num_row = len(topics)

    output_string = ''
    output_string += '\cline{1-2}\n'
    output_string += ('\multirow{' + str(num_row) + '}{*}{' + str(time).split(' ')[0] + '}&')



    first_time = True

    for topic in topics:
        key_words = set(map(lambda x: stemmer.stem(x), topic[0].split(',')))
        #key_words = topic[0].split(',')

        if len(key_words) <= 2: # include ''
            continue

        words = set(map(lambda x: stemmer.stem(x), topic[1].split(',')))
        #words = topic[1].split(',')

        if not first_time:
            output_string += '\n\cline{2-2}\n'
            output_string += '&'
        else:
            first_time = False

        count = 0;
        for word in key_words:
            if len(word) > 0:
                output_string += ('\\textbf{' + word + '},')
                count += 1
                if count >= max_count:
                    break
        for word in words:
            if word not in key_words:
                if len(word) > 0:
                    output_string += (word + ',')
                    count += 1
                    if count >= max_count:
                        break

        output_string = output_string[:-1] + '\\\\'

    return output_string.replace(',', ' ')


def html_bold(_string):
    return '<b>' + _string + '</b>'

import urllib
def html_link(_words, _time, _max_count=10):
    start = _time - datetime.timedelta(hours=12)
    end = _time + datetime.timedelta(hours=12)

    ###
    #start = datetime.datetime.combine(start.date(), datetime.datetime.min.time())
    #end = datetime.datetime.combine(end.date(), datetime.datetime.min.time())
    ###

    _url = "http://10.4.12.100:8080/ts/trackwords.html?int=1&start=" + str(start) + "&end=" + str(end) + "&words="

    _count = 0
    for w in _words:
        if len(w) > 1:
            _url += (urllib.quote(w) + ',')
        _count += 1
        if _count >= _max_count:
            break

    _url += '&dtime=' + str(_time) + '&min=2'

    return '<a href="' + _url + '" target="_blank">'


def to_html_table(time, sig, topics):
    max_count = 9

    # sort
    topics = sorted(topics, key=lambda topic: topic[3], reverse=True)  #  median

    if len(topics) == 0:
        return None

    num_row = 0

    output_string = ''

    first_time = True

    for topic in topics:
        key_words = set(map(lambda x: stemmer.stem(x), topic[0].split(',')))
        original_key_words = topic[0].split(',')
        ''''
        if len(original_key_words) <= 1: # include ''
            continue'''

        words = set(map(lambda x: stemmer.stem(x), topic[1].split(',')))
        original_words = topic[1].split(',')

        if len(original_words) <= 2: # include ''
            continue

        if not first_time:
            output_string += '<tr>\n'
        else:
            first_time = False

        output_string += '<td>\n'

        output_string += html_link(original_words, time, max_count)

        count = 0
        for word in original_key_words:
            if len(word) > 0:
                output_string += (html_bold(word) + ' ')
                count += 1
                if count >= max_count:
                    break
        for word in original_words:
            if word not in key_words:
                if len(word) > 0:
                    output_string += (word + ' ')
                    count += 1
                    if count >= max_count:
                        break

        #output_string = output_string[:-1] + '</a>' + str(topic[3]) + '</td>\n'
        output_string = output_string[:-1] + '</a>' + '</td>\n'

        output_string += '</tr>\n'

        num_row += 1

    if num_row == 0:
        return None

    output_string = '<td rowspan="' + str(num_row) + '">' + str(time) + '</td>\n' + output_string
    output_string = '<tr>\n' + output_string

    return output_string


import process_detection_log
import traceback




def print_results():
    output_list = process_detection_log.process()

    print '====================================='

    sig = dict()
    for thread in output_list:
        sig[thread.start] = (thread.first_keywords, thread.sig)

    #results = get_results('E:/experiment/results/')
    results = get_results('E:/experiment/simple_results/')

    topics = dict()
    for result in results:
        topics[result['time']] = result['topics']#top_topic(result)

    time_list = topics.keys()
    time_list.sort()

    for time in time_list:
        try:
            ''''
            if time not in sig:
                continue
            if sig[time][1] < 2.0:
                print 'pass 2.0'
                continue'''
            #print time, sig[time][1]
            output_string = to_html_table(time, 0.0, topics[time])
            if output_string:
                print output_string
        except:
            #print time, 'error'
            traceback.format_exc()