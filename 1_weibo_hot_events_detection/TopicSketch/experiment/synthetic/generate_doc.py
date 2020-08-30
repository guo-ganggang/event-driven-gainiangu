__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import numpy as np
import scipy.stats

import topic_sketch_plus.stream as stream
import topic_sketch_plus.topic_sketch as tps
import topic_sketch_plus.topic_sketch_plus as tpsp
import fast_smoother
import experiment.examine as examine
import experiment.exp_config as exp_config

import poisson
import hpk

(sq1, rate1) = poisson.simulate(period=600)
sq1 = np.array(sq1)


(sq2, rate2) = hpk.simulate(180)
sq2 = np.array(sq2) + 420



_N_times = 1

_N_words = 10


def create_parameters():

    np.random.seed(327)
    # for bursty topics
    b_alpha = 1e-2*np.ones(_N_words)
    #b_topics = np.random.dirichlet(b_alpha, _N_times)
    b_topics = np.array([[0.4, 0.3, 0.2, 0.1, 0, 0, 0, 0, 0, 0]])

    # for general topics
    g_alpha = 1e-1*np.ones(_N_words)
    #g_topics = np.random.dirichlet(g_alpha, _N_times)
    g_topics = np.array([[0.0, 0.0, 0.0, 0.8, 0.1, 0.1, 0, 0, 0, 0]])


    # for background topics
    _N_back_topics = 4
    back_alpha = np.ones(_N_words)

    back_topics = list()

    for i in xrange(_N_back_topics):
        back_topics.append(np.random.dirichlet(back_alpha, _N_times))

    return b_alpha, g_alpha, b_topics, g_topics, back_topics


b_alpha, g_alpha, b_topics, g_topics, back_topics = create_parameters()

#print b_topics

# for debugging
#print b_topics
#print g_topics
####

def get_doc_len():
    return 50#np.random.poisson(50)

def get_doc(topic):
    doc = ''

    l = get_doc_len()
    word_counts = np.random.multinomial(l, topic)

    for w in xrange(_N_words):
        word_count = word_counts[w]

        for i in xrange(word_count):
            doc += (str(w) + ' ')

    return doc

def get_LDA_doc(alpha, topics):
    theta = np.random.dirichlet(alpha)
    topic = np.dot(topics, theta)

    return get_doc(topic)






def make_old(round, mixture = False, all=0):
    np.random.seed(0)

    topics = np.zeros((_N_words, 2))
    topics[:,0] = b_topics[round,:]
    topics[:,1] = g_topics[round,:]

    t0 = 1425847547.
    one_day = 24 * 60 * 60.


    stream1 = []
    N = 60 * 15
    for i in xrange(N):
        if mixture:
            item = stream.StringItem(t0 + i*one_day/60, get_LDA_doc(np.array([2., 1.]), topics))
        else:
            item = stream.StringItem(t0 + i*one_day/60, get_doc(g_topics[round,:]))
        stream1.append(item)

    stream2 = []
    t = t0 + 13*one_day
    gap = 6*one_day/60
    while t < t0 + N*one_day/60:
        t = t + gap
        gap *= 0.9505
        if mixture:
            item = stream.StringItem(t, get_LDA_doc(np.array([2., 1.]), topics)) ### !!!
        else:
            item = stream.StringItem(t, get_doc(b_topics[round,:]))
        stream2.append(item)

    '''
    stream1 = []
    N = 1000
    for i in xrange(N):
        if mixture:
            item = stream.StringItem(t0, get_LDA_doc(np.array([2., 1.]), topics))
        else:
            item = stream.StringItem(t0, get_doc(g_topics[round,:]))
        stream1.append(item)

    stream2 = []
    for i in xrange(N):
        if mixture:
            item = stream.StringItem(t0, get_LDA_doc(np.array([2., 1.]), topics)) ### !!!
        else:
            item = stream.StringItem(t0, get_doc(b_topics[round,:]))
        stream2.append(item)'''

    if all == 0:
        stream_all = stream1 + stream2
    if all == 1:
        stream_all = stream1
    if all == 2:
        stream_all = stream2

    stream_all.sort(key = lambda x: x.datetime())

    # for debugging
    '''
    for item in stream_all:
        print item.datetime(), item.str'''


    return stream_all



def make(round, mixture=False):
    np.random.seed(0)



    topics_for_b = np.zeros((_N_words, 5))
    topics_for_g = np.zeros((_N_words, 5))
    topics_for_b[:,0] = b_topics[round,:]
    topics_for_g[:,0] = g_topics[round,:]
    for i in xrange(4):
        topics_for_b[:,i + 1] = back_topics[i][round,:]
        topics_for_g[:,i + 1] = back_topics[i][round,:]

    t0 = 1425847547.

    stream1 = []
    for element in sq1:
        if mixture:
            item = stream.StringItem(t0 + 60*element, get_LDA_doc(np.array([5.0, 2.0, 1.0, 1.0, 1.0]), topics_for_g))
        else:
            item = stream.StringItem(t0 + 60*element, get_doc(g_topics[round,:]))
        stream1.append(item)

    stream2 = []
    for element in sq2:
        if mixture:
            item = stream.StringItem(t0 + 60*element, get_LDA_doc(np.array([5.0, 2.0, 1.0, 1.0, 1.0]), topics_for_b))
        else:
            item = stream.StringItem(t0 + 60*element, get_doc(b_topics[round,:]))
        stream2.append(item)

    stream_all = stream1 + stream2
    stream_all = stream1

    stream_all.sort(key=lambda x: x.datetime())

    # for debugging

    for item in stream_all:
        print item.datetime(), item.str


    return stream_all


def entropy(p, q):
    return np.dot(p, np.log(p/q))


def KL(estimated_b_topics):
    KL_dis = np.zeros(_N_times)
    for i in xrange(_N_times):
        KL_dis[i] = scipy.stats.entropy(b_topics[i,:], estimated_b_topics[i,:])
        print KL_dis[i] # for debugging
    return np.mean(KL_dis), KL_dis


def test_random():
    random_b_topics = np.random.dirichlet(b_alpha, _N_times)
    return KL(random_b_topics)

def test_baseline():
    topics = np.ones((_N_times, _N_words)) / _N_words
    return KL(topics)

def test(s):
    _uz = eval(exp_config.get('sketch', 'unit_size'))
    print 'set unit size ' + str(fast_smoother.set_unit_size(_uz))

    if exp_config.get('sketch', 'smoother') == 'XEWMASmoother':
        _wz = eval(exp_config.get('sketch', 'window_size'))
        print 'set XEWMASmoother window ' + str(fast_smoother.XEWMASmoother.set_window_size(_wz))

    if exp_config.get('sketch', 'smoother') == 'EWMASmoother':
        _wz1 = eval(exp_config.get('sketch', 'window_size1'))
        _wz2 = eval(exp_config.get('sketch', 'window_size2'))
        print 'set EWMASmoother window ' + str(fast_smoother.EWMASmoother.set_window_size(_wz1, _wz2))


    sketch = None
    if exp_config.get('sketch', 'type') == 'topicsketch':
        sketch = tps.TopicSketch()
    if exp_config.get('sketch', 'type') == 'topicsketchplus':
        sketch = tpsp.TopicSketchPlus()



    for item in s:
        sketch.process(item)

    if exp_config.get('sketch', 'type') == 'topicsketchplus':
        print 'a', sketch.a

    '''
    m = sketch.plot_sketch('m2', 'a').toarray()

    m = m[50:56, 50:56]

    print m


    p1 = np.array([[0.2, 0.1, 0.0, 0.7, 0.0, 0.0]])
    p1 = p1.T
    p2 = np.array([[0.0, 0.0, 0.0, 0.05, 0.25, 0.7]])
    p2 = p2.T

    #m_ = 18.5 * np.dot(p2, p2.T) + 13.5 * np.dot(p1, p1.T)# 11.6791335802, 0.284346678468
    m_ = 11.6791335802 * np.dot(p2, p2.T) + 0.284346678468 * np.dot(p1, p1.T)

    print m_'''


    _sketch_status = sketch.get_sketch()

    infer_result = examine.simplified_ex(None, _sketch_status, True)[0]

    a = infer_result[0]
    print a
    a = map(lambda x: x.real, a)

    _id = a.index(max(a))
    print 'id', _id

    #debugging
    #print infer_result[2][:_N_words, 0]
    #print infer_result[2][:_N_words, 1]
    ###############

    return infer_result[2][:_N_words, _id]


def refine_prob(_prob):
    #_prob = _prob[:_N_words,1]
    #print _prob[941] # debugging
    prob = _prob.real
    prob = map(lambda x: x if x > 0 else 0, prob)
    prob = np.array(prob) + 1e-10
    prob = prob / sum(prob)
    print prob#debugging
    return prob

def test_topic_sketch_case_a():
    exp_config.set('sketch', 'type', 'topicsketch')
    estimated_topics = np.zeros((_N_times, _N_words))
    for round in xrange(_N_times):
        print 'round', round
        s = make_old(round, False)
        topic = refine_prob(test(s))
        estimated_topics[round, :] = topic
    result = KL(estimated_topics)[0]
    print 'test_topic_sketch_case_a'
    print result

def test_topic_sketch_case_b():
    exp_config.set('sketch', 'type', 'topicsketch')
    estimated_topics = np.zeros((_N_times, _N_words))
    for round in xrange(_N_times):
        print 'round', round
        s = make_old(round, True)
        topic = refine_prob(test(s))
        estimated_topics[round, :] = topic
    result = KL(estimated_topics)[0]
    print 'test_topic_sketch_case_b'
    print result

def test_topic_sketch_plus_case_a():
    exp_config.set('sketch', 'type', 'topicsketchplus')

    _a = 1e2
    results = dict()

    for i in xrange(10):
        print 'alpha0 = ' + str(_a)

        exp_config.set('sketch','alpha0', str(_a))

        estimated_topics = np.zeros((_N_times, _N_words))
        for round in xrange(_N_times):
            print 'round', round
            s = make_old(round, False)
            topic = refine_prob(test(s))
            estimated_topics[round, :] = topic
            #print topic # for debugging
        results[_a] = KL(estimated_topics)[0]

        _a *= 0.1

    print 'test_topic_sketch_plus_case_a'
    for k in sorted(results.keys()):
        print k, results[k]


def test_topic_sketch_plus_case_b():
    exp_config.set('sketch', 'type', 'topicsketchplus')

    _a = 9.
    results = dict()

    for i in xrange(8):
        print 'alpha0 = ' + str(_a)

        exp_config.set('sketch','alpha0', str(_a))

        estimated_topics = np.zeros((_N_times, _N_words))
        for round in xrange(_N_times):
            print 'round', round
            s = make_old(round, True)
            topic = refine_prob(test(s))
            estimated_topics[round, :] = topic
            print topic # for debugging
        results[_a] = KL(estimated_topics)[0]

        #_a *= 0.1
        _a /= 3

    print 'test_topic_sketch_plus_case_b'
    for k in sorted(results.keys()):
        print k, results[k]


import matplotlib.pyplot as plt
import topic_sketch_plus.stream as stream
import topic_sketch_plus.smoother as smoother
def test_topic_sketch_plus():
    '''
    exp_config.set('sketch', 'type', 'topicsketch')

    _a = 3

    for i in xrange(1):
        print 'alpha0 = ' + str(_a)

        exp_config.set('sketch','alpha0', str(_a))

        estimated_topics = np.zeros((_N_times, _N_words))
        for round in xrange(_N_times):
            print 'round', round
            s = make_old(round, False)
            topic = refine_prob(test(s))
            estimated_topics[round, :] = topic
            print topic'''



    sm = smoother.EWMASmoother()
    sm.set_window_size(60., 120.)

    sq = make_old(0, False,1)

    print 'length of sq', len(sq)

    items = []
    for x in sq:
        item = stream.NumberItem(x.timestamp, 1.0)
        items.append(item)

    #output1 = map(lambda item: sm.observe(item)[1], items)
    output2 = map(lambda item: sm.observe(item)[2], items)
    t = map(lambda item: item.datetime(), items)

    #print output2

    #plt.plot(t, output1)
    plt.plot(t, output2)
    plt.show()




