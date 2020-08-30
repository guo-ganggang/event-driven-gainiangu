__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'

import json

import redis

import exp_config

_DEBUG = False

_KEY_EVENT_CHANNEL = 'input a path here'
_KEY_EVENT_PREFIX = _KEY_EVENT_CHANNEL + ':'
_KEY_EVENT_LATEST_EVENT_ID = _KEY_EVENT_PREFIX + 'nextId'
_KEY_EVENT_LATEST_TOPIC_ID = _KEY_EVENT_PREFIX + 'next_topic_Id'
_KEY_EVENT_IDS = _KEY_EVENT_PREFIX + 'ids'
_KEY_EVENT_TIMESTAMPS = _KEY_EVENT_PREFIX + 'timestamps'
_KEY_EVENT_KEYWORDS = _KEY_EVENT_PREFIX + 'keywords'


_HOST = '?'


_eid__ = 0
_tid__ = 0


def get_event_Id():

    if _DEBUG:
        global _eid__
        _eid__ += 1
        return _eid__


    db = redis.StrictRedis(_HOST, port=8181)

    return db.incr(_KEY_EVENT_LATEST_EVENT_ID)


def get_topic_Id():

    if _DEBUG:
        global _tid__
        _tid__ += 1
        return _tid__


    db = redis.StrictRedis(_HOST, port=8181)

    return db.incr(_KEY_EVENT_LATEST_TOPIC_ID)


def put(_id, _event):
    print 'putting ... ' # debugging

    try:
        json_obj = json.dumps(_event)
    except BaseException as e:
        print e
        print _event
        return

    print 'put ' + str(_event['eid']) + '\t' + '\t'.join(_event['info']['words'])
    #print 'detail\t' + json_obj

    if _DEBUG:
        return

    db = redis.StrictRedis(_HOST, port=8181)

    #print 'put:' + '\t' + str(_event)

    # add keywords
    current_keywords = db.lrange(_KEY_EVENT_KEYWORDS, 0, -1)
    if not current_keywords:
        current_keywords = list()
    for word in _event['info']['keywords']:
        if word not in current_keywords:
            print 'pushing keyword', word
            db.rpush(_KEY_EVENT_KEYWORDS, word)

    db.rpush(_KEY_EVENT_IDS, _id)
    db.rpush(_KEY_EVENT_TIMESTAMPS, _event['info']['dtime'])

    key = _KEY_EVENT_PREFIX + str(_id);
    db.set(key, json_obj);



