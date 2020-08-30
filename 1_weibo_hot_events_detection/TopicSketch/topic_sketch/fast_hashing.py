__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import os
from ctypes import cdll

if os.name == 'posix':
    hashBase = cdll.LoadLibrary('./c/ghf.so')
if os.name == 'nt':
    hashBase = cdll.LoadLibrary('./c/ghf.dll')


HASH_NUMBER = 5

def hash_code(txt):
    l = len(txt)
    l = min(32, l)

    ret = [
        hashBase.BKDRHash(txt, l),
        hashBase.APHash(txt, l),
        hashBase.DJBHash(txt, l),
        hashBase.JSHash(txt, l),
        hashBase.RSHash(txt, l)
    ]

    return ret

