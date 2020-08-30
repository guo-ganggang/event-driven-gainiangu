__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import math
from collections import deque

import numpy

import fast_smoother

_ONE_MINUTE = 60 # seconds






class Smoother:

    def observe(self, _item):
    # observe a new incoming item, and return current status.
    # NOTE : item must be in order of time !!!!!!!
        pass

    def get(self, _timestamp):
    # return current status
        pass



def smooth(_item_stream, _smoother):

    statuses = []

    item = _item_stream.next()
    while item :
        statuses.append(_smoother.observe(item))
        item = _item_stream.next()

    return statuses


class MASmoother(Smoother): # Moving Average Smoother

    _WINDOW_SIZE = 15

    @classmethod
    def set_window_size(cls, _wz):
        cls._WINDOW_SIZE = _wz

    def __init__(self):
        self.v = 0
        self.a = 0
        self.timestamp = 0
        self.queue1 = deque([])
        self.queue2 = deque([])

    def observe(self, _item): # observe a new incoming item, and return current status

        self.timestamp = _item.timestamp

        self.queue1.append(_item)

        item = self.queue1[0]
        while item.timestamp + self._WINDOW_SIZE * _ONE_MINUTE < self.timestamp:
            self.queue2.append(self.queue1.popleft())
            item = self.queue1[0]

        if len(self.queue2) > 0:
            item = self.queue2[0]
            while item.timestamp + 2 * self._WINDOW_SIZE * _ONE_MINUTE < self.timestamp:
                self.queue2.popleft()
                if len(self.queue2) == 0:
                    break
                item = self.queue2[0]

        self.v = sum(map(lambda x: x.number, self.queue1))

        self.a = self.v - sum(map(lambda x: x.number, self.queue2))

        self.v /= self._WINDOW_SIZE
        self.a /= (self._WINDOW_SIZE * self._WINDOW_SIZE)

        return _item.timestamp, self.v, self.a

    def get(self, _timestamp):  # return current status
        queue = list(self.queue1) + list(self.queue2)

        v = sum(map(lambda x: (x.timestamp + self._WINDOW_SIZE >= _timestamp) * x.number, queue))

        a = sum(map(lambda x: (x.timestamp + self._WINDOW_SIZE >= self.timestamp) * x.number, queue))

        a -= sum(map(lambda x: ((x.timestamp + self._WINDOW_SIZE < self.timestamp) and
                                (x.timestamp + 2 * self._WINDOW_SIZE >= self.timestamp)) * x.number, queue))

        v /= self._WINDOW_SIZE
        a /= (self._WINDOW_SIZE * self._WINDOW_SIZE)

        return _timestamp, v,  a


class EWMASmoother(Smoother): # Exponentially Weighted Moving Average Smoother

    _WINDOW_SIZE1 = 15

    _WINDOW_SIZE2 = 16

    @classmethod
    def set_window_size(cls, _wz1, _wz2):
        cls._WINDOW_SIZE1 = _wz1
        cls._WINDOW_SIZE2 = _wz2

    def __init__(self):
        self.v1 = 0
        self.v2 = 0
        self.timestamp = 0

    def observe(self, _item): # observe a new incoming item, and return current status

        if self.timestamp != 0:
            dt = (self.timestamp - _item.timestamp) / _ONE_MINUTE
            e1 = math.exp(dt/self._WINDOW_SIZE1)
            e2 = math.exp(dt/self._WINDOW_SIZE2)
            self.v1 *= e1
            self.v2 *= e2

        self.timestamp = _item.timestamp

        self.v1 += _item.number/self._WINDOW_SIZE1
        self.v2 += _item.number/self._WINDOW_SIZE2

        return _item.timestamp, self.v1, (self.v1 - self.v2)/(self._WINDOW_SIZE2 - self._WINDOW_SIZE1)


    def get(self, _timestamp): # return current status

        if _timestamp < self.timestamp:
            return None

        dt = (self.timestamp - _timestamp) / _ONE_MINUTE

        e1 = math.exp(dt/self._WINDOW_SIZE1)
        e2 = math.exp(dt/self._WINDOW_SIZE2)

        return _timestamp, e1 * self.v1, (e1 * self.v1 - e2 * self.v2)/(self._WINDOW_SIZE2 - self._WINDOW_SIZE1)


class XEWMASmoother(Smoother): # extend EWMASmoother by using smooth function $x*exp(-x/T)$

    _WINDOW_SIZE = 15

    @classmethod
    def set_window_size(cls, _wz):
        cls._WINDOW_SIZE = _wz

    def __init__(self):
        self.x = numpy.zeros((4,1))
        self.timestamp = 0

    @staticmethod
    def _weight_matrix(dt):
        mat = numpy.eye(4)
        mat[1, 0] = dt
        mat[2, 0] = dt*dt
        mat[2, 1] = 2*dt
        mat[3, 0] = dt*dt*dt
        mat[3, 1] = 3*dt*dt
        mat[3, 2] = 3*dt
        return mat

    def observe(self, _item): # observe a new incoming item, and return current status
        if self.timestamp != 0:
            dt = (self.timestamp - _item.timestamp) / _ONE_MINUTE
            e = math.exp(dt/self._WINDOW_SIZE)
            self.x = e * numpy.dot(self._weight_matrix(-dt), self.x)

        self.timestamp = _item.timestamp

        b = numpy.zeros((4,1))
        b[0, 0] = _item.number

        self.x = self.x + b

        v = self.x[1] / (self._WINDOW_SIZE ** 2)

        a = (3*self._WINDOW_SIZE*self.x[2] - self.x[3]) / (6 * self._WINDOW_SIZE ** 5)

        return _item.timestamp, v,  a

    def get(self, _timestamp): # return current status
        if _timestamp < self.timestamp:
            return None

        dt = (self.timestamp - _timestamp) / _ONE_MINUTE

        e = math.exp(dt/self._WINDOW_SIZE)

        x_ = e * numpy.dot(self._weight_matrix(-dt), self.x)

        v = x_[1] / (self._WINDOW_SIZE ** 2)

        a = (3*self._WINDOW_SIZE*x_[2] - x_[3]) / (6 * self._WINDOW_SIZE ** 5)

        return _timestamp, v, a


class FastXEWMASmoother(Smoother): # fast version of XEWMASmoother

    @classmethod
    def set_window_size(cls, _wz):
        fast_smoother.XEWMASmoother.set_window_size(_wz)

    def __init__(self):
        self.smoother = fast_smoother.XEWMASmoother()

    def observe(self, _item): # observe a new incoming item, and return current status
        return self.smoother.observe(_item.timestamp, _item.number)

    def get(self, _timestamp): # return current status
        return self.smoother.get(_timestamp)