__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

'''Homogeneous Poisson'''

import numpy as np

def simulate(r=0.1, period=1000):
    np.random.seed(327)

    t = 0
    history = list()
    rate = list()
    history.append(t)
    rate.append(r)

    while t < period:
        t += np.random.exponential(1./r)
        history.append(t)
        rate.append(r)

    return history, rate


