__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import redis
import exp_config

_KEY_MONITOR_CHANNEL = 'twitter:sg:event:python:monitor_ab_test:a'
_HOST = exp_config.get('stream', 'host')

print '_KEY_MONITOR_CHANNEL', _KEY_MONITOR_CHANNEL

### clear memory ########
db = redis.StrictRedis(_HOST, port=8181)
db.delete(_KEY_MONITOR_CHANNEL)
#########################

def report_rate(t, r):
    if not _KEY_MONITOR_CHANNEL:
        return
    db = redis.StrictRedis(_HOST, port=8181)
    db.lpush(_KEY_MONITOR_CHANNEL, (t, r))