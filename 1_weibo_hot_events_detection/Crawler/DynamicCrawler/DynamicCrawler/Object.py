from datetime import datetime


class AccountParameters(object):

    def __init__(self, i, s, gsid, domain, account):
        self.i = i
        self.s = s
        self.gsid = gsid
        self.count = 0
        self.domain = domain
        self.account = account


class TargetUser(object):

    def __init__(self, uid, weight, domain, subdomain):
        self.uid = uid
        self.weight = weight
        self.domain = domain
        self.subdomain = subdomain


class Timeline(object):

    def __init__(self, dict):
        self.mid = dict['mid']
        self.uid = dict['uid']
        self.name = dict['name']

        self.omid = dict['omid']
        self.ouid = dict['ouid']
        self.oname = dict['oname']

        self.text = dict['text']
        self.created_at = dict['created_at']
        self.app_source = dict['app_source']

        self.repost_num = dict['repost_num']
        self.favourite_num = dict['favourite_num']
        self.comment_num = dict['comment_num']

        self.geo_info = dict['geo_info']
        self.timestamp = dict['timestamp']

        self.pic_url = dict['pic_url']


class Alarm(object):

    def __init__(self, domain, is_on=1, launch_time=datetime.now()):
        self.domain = domain
        self.is_on = is_on
        self.launch_time = launch_time


class TestMerge(object):
    def __init__(self, id, value):
        self.id = id
        self.value = value


class Profile(object):
    """
    Mapped to User in Database.py
    """
    def __init__(self, dict):
        for key, value in dict.items():
            setattr(self, key, value)

