__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

'''Hawkes Process'''

import math
from collections import deque
import numpy as np


_lambda = 0.001
_delta = 0.1
_alpha = 0.5

def get_hp(n):
    ret = []

    s = 0.
    t = 0.
    for i in xrange(n):
        dt = np.random.exponential(1./(_lambda + s))
        if t == 0:
            t0 = dt
        t += dt
        s = s * math.exp(-_delta * dt) + _alpha * math.exp(-0.020*(t-t0))
        ret.append(t)

    return ret

'''
bandwidth = 6.


def decay(t):
    return 0.25*math.exp(- (t/bandwidth))

class Status:

    def __init__(self):
        self.observations = deque()

    def observe(self, t):
        self.observations.append(t)

    def current(self, t):
        ret = 0.0

        _n = 0
        for t0 in self.observations:
            pulse = decay(t - t0)
            if pulse < 1e-3:
                _n += 1
            ret += pulse

        for i in xrange(_n):
            self.observations.popleft()

        return ret


def get_hp(n):
    ret = list()

    t = 0.0
    dt = 0.01
    s = Status()

    s.observe(t)
    t += dt
    while True:
        prob = s.current(t) * dt
        if np.random.rand() < prob:
            s.observe(t)
            ret.append(t)
        t += dt

        if len(ret) >= n or t >= 24*60*60:
            return ret
'''


#################### for testing ###################
import matplotlib.pyplot as plt
import topic_sketch_plus.stream as stream
import topic_sketch_plus.smoother as smoother
def _test():
    #plt.axis([0, 5000, 0, 120])
    for i in xrange(1):
        sq = get_hp(1000)

        sm = smoother.EWMASmoother()
        sm.set_window_size(1, 2)
        items = []
        for x in sq:
            item = stream.NumberItem(x, 1.0)
            items.append(item)

        output = map(lambda item: sm.observe(item)[1], items)

        plt.plot(np.array(sq),output)
    plt.show()


_test()



