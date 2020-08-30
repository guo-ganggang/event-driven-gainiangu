from utilities import reset_dict
from models import Timeline
from bs4 import BeautifulSoup
from datetime import datetime
import json


class Parser(object):
    def __init__(self):
        self.timelines = []
        self.timeline = {
            'mid': '',
            'encrypted_mid': '',
            'uid': '',
            'screen_name': '',
            'text': '',
            'app_source': '',
            'created_at': '',
            'attitudes': '',
            'comments': '',
            'reposts': '',
            'pic_urls': '',
            'json': '',
            'timestamp': '',
            'omid': ''
        }
        self.origin_timeline = {
            'mid': '',
            'encrypted_mid': '',
            'uid': '',
            'screen_name': '',
            'text': '',
            'app_source': '',
            'created_at': '',
            'attitudes': '',
            'comments': '',
            'reposts': '',
            'pic_urls': '',
            'json': '',
            'timestamp': '',
            'omid': ''
        }

    def parse_timelines(self, all_cards):
        """

        :param all_cards:  a list
        :return:
        """
        result_set = []

        for cards in all_cards:
            itemid = cards['itemid']
            if itemid == 'mblog':
                cards = cards['card_group']
            else:
                continue

            self.parse_cards(cards)

        result_set = self.timelines
        self.timelines = []  # release memory
        return result_set

    def parse_cards(self, cards):
        """

        :param cards: a list
        :return:
        """
        for card in cards:
            self.parse_card(card)

    def parse_mid(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        return mblog['id']

    def parse_encrypted_mid(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        return mblog['mblogid']

    def parse_uid(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        user = mblog['user']
        if not isinstance(user, dict):
            return -1
        else:
            return user['id']

    def parse_screen_name(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        return mblog['user']['screen_name']

    def parse_text(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        return mblog['text']

    def parse_app_source(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        app = mblog['source']
        soup = BeautifulSoup(app)
        app = soup.text

        return app

    def parse_created_at(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        date = mblog['created_at']
        date = datetime.strptime(date, '%a %b %d %X +0800 %Y')

        return date

    def parse_attitudes(self, mblog):
        """

        :param mblog:  a dict
        :return:
        """
        try:
            return mblog['attitudes_count']
        except KeyError:
            return 0

    def parse_comments(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        try:
            return mblog['comments_count']
        except KeyError:
            return 0

    def parse_reposts(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        try:
            return mblog['reposts_count']
        except KeyError:
            return 0

    def parse_pic_urls(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        try:
            urls = mblog['pic_ids']
        except KeyError:
            return ''
        pics = u''

        for url in urls:
            pics += url + u', '

        pics = pics.strip(u', ')

        return pics

    def parse_json(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        jsn = json.dumps(mblog)
        return jsn

    def parse_card(self, card):
        """

        :param card: a dict
        :return:
        """
        mblog = card['mblog']
        reset_dict(self.timeline)  # initialization

        self.timeline['uid'] = self.parse_uid(mblog)
        if self.timeline['uid'] == -1:
            return -1  # No access to this post

        self.timeline['mid'] = self.parse_mid(mblog)
        self.timeline['encrypted_mid'] = self.parse_encrypted_mid(mblog)
        self.timeline['screen_name'] = self.parse_screen_name(mblog)
        self.timeline['text'] = self.parse_text(mblog)
        self.timeline['app_source'] = self.parse_app_source(mblog)
        self.timeline['created_at'] = self.parse_created_at(mblog)
        self.timeline['attitudes'] = self.parse_attitudes(mblog)
        self.timeline['comments'] = self.parse_comments(mblog)
        self.timeline['reposts'] = self.parse_reposts(mblog)
        self.timeline['pic_urls'] = self.parse_pic_urls(mblog)
        self.timeline['json'] = self.parse_json(mblog)
        self.timeline['timestamp'] = datetime.now()

        self.timeline['omid'] = self.parse_omid(mblog)
        if self.timeline['omid'] != 0:
            self.parse_origin_timeline(mblog)
            self.timeline['text'] = u'%s //@%s:%s' % (
                self.timeline['text'],
                self.origin_timeline['screen_name'],
                self.origin_timeline['text']
            )
            self.timeline['pic_urls'] = u'%s, %s' % (
                self.timeline['pic_urls'],
                self.origin_timeline['pic_urls']
            )
            self.timeline['pic_urls'].strip(u', ')
            self.timelines.append(Timeline(**self.origin_timeline))

        self.timelines.append(Timeline(**self.timeline))

        return 0

    def parse_omid(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        try:
            origin_post = mblog['retweeted_status']
        except KeyError:
            return 0

        return origin_post['mid']

    def parse_origin_mid(self, origin_post):
        return origin_post['mid']

    def parse_origin_encrypted_mid(self, origin_post):
        return origin_post['mblogid']

    def parse_origin_uid(self, origin_post):
        return origin_post['user']['id']

    def parse_origin_screen_name(self, origin_post):
        return origin_post['user']['screen_name']

    def parse_origin_text(self, origin_post):
        return origin_post['text']

    def parse_origin_app_source(self, origin_post):
        app = origin_post['source']
        soup = BeautifulSoup(app)
        app = soup.text

        return app

    def parse_origin_created_at(self, origin_post):
        date = origin_post['created_at']
        date = datetime.strptime(date, '%a %b %d %X +0800 %Y')

        return date

    def parse_origin_attitudes(self, origin_post):
        try:
            return origin_post['attitudes_count']
        except KeyError:
            return 0

    def parse_origin_comments(self, origin_post):
        try:
            return origin_post['comments_count']
        except KeyError:
            return 0

    def parse_origin_reposts(self, origin_post):
        try:
            return origin_post['reposts_count']
        except KeyError:
            return 0

    def parse_origin_pic_urls(self, origin_post):
        try:
            urls = origin_post['pic_ids']
        except KeyError:
            return ''
        pics = u''

        for url in urls:
            pics += url + u', '

        pics = pics.strip(u', ')

        return pics

    def parse_origin_timeline(self, mblog):
        """

        :param mblog: a dict
        :return:
        """
        origin_post = mblog['retweeted_status']
        reset_dict(self.origin_timeline)
        self.origin_timeline['omid'] = 0

        self.origin_timeline['mid'] = self.parse_origin_mid(origin_post)
        self.origin_timeline['encrypted_mid'] = self.parse_origin_encrypted_mid(origin_post)
        self.origin_timeline['uid'] = self.parse_origin_uid(origin_post)
        self.origin_timeline['screen_name'] = self.parse_origin_screen_name(origin_post)
        self.origin_timeline['text'] = self.parse_origin_text(origin_post)
        self.origin_timeline['app_source'] = self.parse_origin_app_source(origin_post)
        self.origin_timeline['created_at'] = self.parse_origin_created_at(origin_post)
        self.origin_timeline['attitudes'] = self.parse_origin_attitudes(origin_post)
        self.origin_timeline['comments'] = self.parse_origin_comments(origin_post)
        self.origin_timeline['reposts'] = self.parse_origin_reposts(origin_post)
        self.origin_timeline['pic_urls'] = self.parse_origin_pic_urls(origin_post)
        self.origin_timeline['json'] = ''  # its json data is stored in timeline['json']
        self.origin_timeline['timestamp'] = datetime.now()