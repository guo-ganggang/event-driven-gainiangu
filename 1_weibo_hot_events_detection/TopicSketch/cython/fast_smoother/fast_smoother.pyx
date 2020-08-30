__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'



from libc.math cimport exp



cdef int _ONE_UNIT = 60 # seconds


cdef double _WINDOW_SIZE = 15.

cdef double _WINDOW_SIZE1 = 15.

cdef double _WINDOW_SIZE2 = 16.


def set_unit_size(int _uz):
    global _ONE_UNIT

    _ONE_UNIT = _uz
    return _ONE_UNIT

cdef class XEWMASmoother: # extend EWMASmoother by using smooth function $x*exp(-x/T)$

    cdef double[4] x
    cdef public double timestamp

    @staticmethod
    def set_window_size(double _wz):
        global _WINDOW_SIZE

        _WINDOW_SIZE = _wz
        return _WINDOW_SIZE

    def __init__(self):
        cdef int i
        for i in range(4):
            self.x[i] = 0.0

        self.timestamp = 0.0

    @staticmethod
    def _weight_matrix(double _dt, double[:,:] mat):

        cdef int i, j

        cdef double dt = _dt

        for i in range(4):
            mat[i][i] = 1.0

        mat[1, 0] = dt
        mat[2, 0] = dt*dt
        mat[2, 1] = 2*dt
        mat[3, 0] = dt*dt*dt
        mat[3, 1] = 3*dt*dt
        mat[3, 2] = 3*dt


    @staticmethod
    def _multiply(double _e, double[:,:] _mat, double[:] _vec, double[:] ret):
        cdef int i, j
        for i in range(4):
            ret[i] = 0.0
            for j in range(i + 1):
                ret[i] += _mat[i,j] * _vec[j]
            ret[i] *= _e


    def copy(self, double[:] _vec):
        cdef int i
        for i in range(4):
            self.x[i] = _vec[i]

    def observe(self, double _timestamp, double _number): # observe a new incoming item, and return current status
        global _WINDOW_SIZE
        global _ONE_UNIT

        cdef double dt, e, v, a

        cdef double[4][4] mat
        cdef double[4] x_
        cdef double[:,:] point_mat
        cdef double[:] point_x_, point_x

        if self.timestamp != 0:
            dt = (self.timestamp - _timestamp) / _ONE_UNIT

            if dt != 0:

                e = exp(dt/_WINDOW_SIZE)

                point_mat = mat
                point_x_ = x_
                point_x = self.x
                self._weight_matrix(-dt, point_mat)
                self._multiply(e, point_mat, point_x, point_x_)
                self.copy(point_x_)

        self.timestamp = _timestamp

        self.x[0] += _number

        v = self.x[1] / (_WINDOW_SIZE ** 2)

        a = (3*_WINDOW_SIZE*self.x[2] - self.x[3]) / (6 * _WINDOW_SIZE ** 5)

        return _timestamp, v,  a

    def get(self, _timestamp): # return current status
        global _WINDOW_SIZE
        global _ONE_UNIT

        cdef double dt, e, v, a
        cdef double[4][4] mat
        cdef double[4] x_
        cdef double[:,:] point_mat
        cdef double[:] point_x_, point_x

        if _timestamp < self.timestamp:
            return None

        dt = (self.timestamp - _timestamp) / _ONE_UNIT


        if dt == 0:
            v = self.x[1] / (_WINDOW_SIZE ** 2)

            a = (3*_WINDOW_SIZE*self.x[2] - self.x[3]) / (6 * _WINDOW_SIZE ** 5)

            return _timestamp, v, a

        e = exp(dt/_WINDOW_SIZE)

        point_mat = mat
        point_x_ = x_
        point_x = self.x
        self._weight_matrix(-dt, point_mat)
        self._multiply(e, point_mat, point_x, point_x_)

        v = x_[1] / (_WINDOW_SIZE ** 2)

        a = (3*_WINDOW_SIZE*x_[2] - x_[3]) / (6 * _WINDOW_SIZE ** 5)

        return _timestamp, v, a

    def get_plus(self, _timestamp): # return current status
        global _WINDOW_SIZE
        global _ONE_UNIT

        cdef double dt, e, r
        cdef double[4][4] mat
        cdef double[4] x_
        cdef double[:,:] point_mat
        cdef double[:] point_x_, point_x

        if _timestamp < self.timestamp:
            return None

        dt = (self.timestamp - _timestamp) / _ONE_UNIT

        e = exp(dt/_WINDOW_SIZE)

        point_mat = mat
        point_x_ = x_
        point_x = self.x
        self._weight_matrix(-dt, point_mat)
        self._multiply(e, point_mat, point_x, point_x_)

        r = x_[0] / (_WINDOW_SIZE ** 2) - x_[1] / (_WINDOW_SIZE ** 3)

        return _timestamp, r

    def peek_x(self):
        return self.x[0], self.x[1], self.x[2], self.x[3]


cdef class EWMASmoother: # Exponentially Weighted Moving Average Smoother

    cdef public double v1, v2
    cdef public double timestamp

    @staticmethod
    def set_window_size(double _wz1, double _wz2):
        global _WINDOW_SIZE1
        global _WINDOW_SIZE2

        _WINDOW_SIZE1 = _wz1
        _WINDOW_SIZE2 = _wz2

        return _WINDOW_SIZE1, _WINDOW_SIZE2

    def __init__(self):
        self.v1 = 0
        self.v2 = 0
        self.timestamp = 0

    def observe(self, double _timestamp, double _number): # observe a new incoming item, and return current status
        global _WINDOW_SIZE1
        global _WINDOW_SIZE2

        cdef double e1, e2, dt

        if self.timestamp != 0:
            dt = (self.timestamp - _timestamp) / _ONE_UNIT

            if dt != 0:
                e1 = exp(dt/_WINDOW_SIZE1)
                e2 = exp(dt/_WINDOW_SIZE2)
                self.v1 *= e1
                self.v2 *= e2

        self.timestamp = _timestamp

        self.v1 += _number/_WINDOW_SIZE1
        self.v2 += _number/_WINDOW_SIZE2

        return _timestamp, self.v1, (self.v1 - self.v2)/(_WINDOW_SIZE2 - _WINDOW_SIZE1)


    def get(self, double _timestamp): # return current status
        global _WINDOW_SIZE1
        global _WINDOW_SIZE2

        cdef double e1, e2, dt

        if _timestamp < self.timestamp:
            return None

        dt = (self.timestamp - _timestamp) / _ONE_UNIT

        if dt == 0:
            return _timestamp, self.v1, (self.v1 - self.v2)/(_WINDOW_SIZE2 - _WINDOW_SIZE1)

        e1 = exp(dt/_WINDOW_SIZE1)
        e2 = exp(dt/_WINDOW_SIZE2)

        return _timestamp, e1 * self.v1, (e1 * self.v1 - e2 * self.v2)/(_WINDOW_SIZE2 - _WINDOW_SIZE1)