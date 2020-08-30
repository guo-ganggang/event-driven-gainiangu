from downloader import Downloader
from parser import Parser
from timer import Timer
from utilities import mode_add_one
from configs import ACC_ACCESS_LIMIT, ACC_RESET_TIME
import time
from daos import Account, Keyword, Timeline


class Crawler(object):
    def __init__(self):
        self.keywords = Keyword.get_keywords()
        self.timelines = []

        self.downloader = Downloader()
        self.parser = Parser()
        self.life_timer = Timer()

        self.accounts = Account.get_accounts()
        self.account = None
        self.acc_index = 0
        self.acc_timer = None

    def init_account(self):
        if self.account is not None:
            return 1
        self.account = self.accounts[self.acc_index]
        self.acc_index = mode_add_one(self.acc_index, len(self.accounts))
        self.acc_timer = Timer()
        print 'Loading account:%s ...' % (self.account.username,)

    def change_account(self):
        index = self.acc_index
        while True:
            self.account = self.accounts[self.acc_index]
            self.acc_index = mode_add_one(self.acc_index, len(self.accounts))
            if self.account.count > ACC_ACCESS_LIMIT:
                if self.acc_index == index:
                    self.reset_accounts()
                continue

            print 'Change to account-%s ...' % (self.account.username,)
            return 0

    def reset_accounts(self):
        while True:
            elapsed_time = self.acc_timer.click()
            if elapsed_time > ACC_RESET_TIME:
                for account in self.accounts:
                    account.count = 0
                print 'Reset all the accounts...'
                self.acc_timer.reset()
                return 0
            else:
                sleep = ACC_RESET_TIME - elapsed_time + 5
                print 'Sleep %d seconds...' % (sleep,)
                time.sleep(sleep)

    def dump_timelines(self):
        print 'Dumping timelines to database...'
        Timeline.dump(self.timelines)
        self.timelines = []  # release memory

    def parse_timelines(self, timeline_panel):
        return self.parser.parse_timelines(timeline_panel)

    def download_one_page_timelines(self, keyword, page):
        while True:
            timeline_panel = self.downloader.download(self.account, keyword, page)

            if timeline_panel is None:
                self.change_account()
                continue

            return timeline_panel

    def download_related_timelines(self, keyword):
        all_cards = []
        page = 1

        while True:
            print 'Getting page %d...' % (page,)
            timeline_panel = self.download_one_page_timelines(keyword, page)

            try:
                cards = timeline_panel['cards']
            except KeyError:
                print 'Dirty data...'
                continue
            if len(cards) == 0:
                return all_cards
            else:
                all_cards.extend(cards)
                page += 1

    def search_and_get_related_timelines(self):
        self.init_account()

        for keyword in self.keywords:
            keyword = keyword.keyword
            print 'Get timelines about "%s"' % (keyword,)
            all_cards = self.download_related_timelines(keyword)
            timelines = self.parse_timelines(all_cards)
            self.timelines.extend(timelines)
            self.dump_timelines()

    def update_keywords(self):
        print 'Updating keywords...'
        Keyword.disable_keywords(self.keywords)
        self.keywords = Keyword.get_keywords()



