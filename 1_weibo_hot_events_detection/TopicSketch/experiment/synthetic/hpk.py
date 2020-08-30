__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


'''Hawkess Process with gaussian Kernels'''


import numpy as np


def kernel(x, mu, sigma):

    ret = - (x - mu) ** 2
    ret /= 2 * (sigma ** 2)
    ret = np.exp(ret)
    ret /= sigma
    ret /= np.sqrt(2*np.pi)

    return ret

def max_kernel(x, mu, sigma):
    return (x <= mu) * kernel(mu, mu, sigma) + (x > mu) * kernel(x, mu, sigma)

def combined_kernel(x, mus, sigmas, weights):

    ret = sum(map(lambda mu, sigma, weight: weight * kernel(x, mu, sigma), mus, sigmas, weights))
    return ret



def simulate(period=1000, seed = 1):
    np.random.seed(327*seed)

    mus = [4., 16., 64.]
    sigmas = [4., 16., 64.]
    weights = 0.50*np.array([0.03, 0.051, 0.0001])* np.sqrt(2*np.pi) * np.array([4., 16., 64.])

    t = 0
    history = list()
    rate = list()
    history.append(t)
    rate.append(sum(combined_kernel(t - np.array(history), mus, sigmas, weights)))

    n_sample = 0
    while t < period:
        # thinning
        W = sum(sum(map(lambda mu, sigma, weight: weight * max_kernel(t - np.array(history), mu, sigma), mus, sigmas, weights)))
        print 'W', W
        next_t = 0
        while True:
            next_t += np.random.exponential(1./W)
            n_sample += 1
            if n_sample >= 10000:
                break
            threshold = sum(combined_kernel(t + next_t - np.array(history), mus, sigmas, weights)) / W
            print 'threshold', threshold
            if np.random.random() <= threshold:
                break
        if n_sample >= 10000:
            break
        t = t + next_t
        print 't', t
        history.append(t)
        rate.append(sum(combined_kernel(t - np.array(history), mus, sigmas, weights)))

    return history, rate







