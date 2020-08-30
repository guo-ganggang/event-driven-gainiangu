__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import ConfigParser

config = ConfigParser.ConfigParser()
config.read("./experiment/twitter.cnf")

def get(_section, _option):
    return config.get(_section, _option)

def set(_section, _option, _value):
    config.set(_section, _option, _value)

for s in config.sections():
    print '[' + s + ']'
    for x in config.options(s):
        print '\t' + x + ':' + config.get(s, x)