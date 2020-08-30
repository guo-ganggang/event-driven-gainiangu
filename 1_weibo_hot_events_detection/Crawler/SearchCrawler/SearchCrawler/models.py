class Account(object):
    def __init__(self, **account):
        self.username = account['username']
        self.password = account['password']
        self.s = account['s']
        self.gsid = account['gsid']
        self.cid = account['cid']  # crawler id

        self.count = 0


class Timeline(object):
    def __init__(self, **timeline):
        self.mid = timeline['mid']
        self.encrypted_mid = timeline['encrypted_mid']
        self.uid = timeline['uid']
        self.screen_name = timeline['screen_name']
        self.text = timeline['text']
        self.app_source = timeline['app_source']
        self.created_at = timeline['created_at']
        self.attitudes = timeline['attitudes']
        self.comments = timeline['comments']
        self.reposts = timeline['reposts']
        self.pic_urls = timeline['pic_urls']
        self.json = timeline['json']
        self.timestamp = timeline['timestamp']

        self.omid = timeline['omid']


class Keyword(object):
    def __init__(self, **keyword):
        self.keyword = keyword['keyword']
        self.cid = keyword['cid']
        self.score = keyword['score']
        self.timestamp = keyword['timestamp']
