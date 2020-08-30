import Getter
import Parser
from Database import TargetUser, AccountParameters, Timelines, Alarm, User
from Timer import Timer
from Configuration import ACCESS_LIMIT, ACCESS_TIME_WINDOW, TIME_WINDOW, LOOP_TIME, THRESHOLD, DECAY_TIME, REST
from Configuration import SUBDOMAIN, DOMAIN2, DOMAIN, DOMAIN3, PROFILE_LIMIT, ACCOUNT_LIMIT, TIMELINE_EARLIEST_DATETIME
from Configuration import MIN_DM, MAX_DM, BUFFER_LIMIT_LARGE
import Utility
from datetime import datetime
import time
import json
from Configuration import BUFFER_LIMIT, BUFFER_LIMIT_MINI, PROFILE_BUFFER_LIMIT


class Crawler(object):

    def __init__(self):
        self.running_mode = None
        # 1 for monitoring, 2 for reinforcing, 3 for history crawling

        self.getter = Getter.Getter()
        self.parser = Parser

        self.targets = []
        self.accounts = None
        self.account_index = 0
        self.running_account = None
        self.memory = []
        self.buffer = []

        self.account_timer = None
        self.alarm_timer = None
        self.account_management_timer = Timer()

        self.user_list = []  # targets to crawl, only uid stored
        self.profile_list = []  # where user profiles stored

        self.earliest_time = self.parse_earliest_time(TIMELINE_EARLIEST_DATETIME)

    def parse_earliest_time(self, earlist_time_str):
        """
        Convert a datetime string to a datetime object
        :param earlist_time_str: a datetime string
        :return:  a datetime object
        """
        dt = earlist_time_str.split('-')
        year = int(dt[0])
        month = int(dt[1])
        day = int(dt[2])

        return datetime(year, month, day)

    def ban_account(self, flag=-1):
        '''

        :param flag: -1 means wrong password
        :return:
        '''
        AccountParameters.ban(self.running_account, flag)
        self.accounts.pop(self.account_index)
        if self.account_index == len(self.accounts):
            self.account_index -= 1

    def reset_buffer(self):
        """
        reset buffer via flushing data into database
        :return:
        """

        Timelines.dump(self.buffer)
        self.buffer = []

        User.dumps(self.profile_list)
        self.profile_list = []

        print 'Reset buffer and dump data into DB!'

    def reset_accounts(self):
        """
        Reset all the accounts
        :return:
        """
        self.account_timer.reset()

        day = self.account_management_timer.click().days
        if day > 0:
            self.account_management_timer.reset()
            AccountParameters.reset403()

        if len(self.accounts) < ACCOUNT_LIMIT:
            if self.running_mode == 1:
                AccountParameters.supplement_account(DOMAIN)
                self.accounts = AccountParameters.get_account_parameters(DOMAIN)
            elif self.running_mode == 2:
                AccountParameters.supplement_account(DOMAIN2)
                self.accounts = AccountParameters.get_account_parameters(DOMAIN2)
            elif self.running_mode == 3:
                AccountParameters.supplement_account(DOMAIN3)
                self.accounts = AccountParameters.get_account_parameters(DOMAIN3)
            return 0

        for acc in self.accounts:
            acc.count = 0

    def try_update_account(self):
        """
        Try to update account
        If all the accounts are not ready, it will waits until they get ready
        :return:
        """
        while True:
            elapsed_time = self.account_timer.click()
            if elapsed_time.seconds > ACCESS_TIME_WINDOW:
                self.reset_accounts()
                break
            else:
                sleep_time = ACCESS_TIME_WINDOW - elapsed_time.seconds + 2
                # add 2 seconds to keep waken at the best time point
                print "It's going to sleep %d seconds!" % (sleep_time,)
                time.sleep(sleep_time)

    def get_account(self):
        """
        get the correct account
        :return:
        """
        flag = self.account_index
        while True:
            account = self.accounts[self.account_index]
            if account.count > ACCESS_LIMIT:
                self.account_index = Utility.loop_increase(self.account_index, len(self.accounts))
            else:
                return account

            if self.account_index == flag:
                self.try_update_account()

    def update_account(self):
        elapsed_time = self.account_timer.click()

        if elapsed_time.seconds > ACCESS_TIME_WINDOW:  # reset all the accounts
            self.reset_accounts()
            print 'Reset all the account!'
        self.account_index = Utility.loop_increase(self.account_index, len(self.accounts))
        return self.get_account()

    def download_timelines(self, uid, page=1):
        while True:
            timeline_pannel = self.getter.get_user_timeline(uid, self.running_account, page)

            if timeline_pannel == None:
                self.running_account = self.update_account()
                print 'Change account to %s due to NO TIMELINES!' % (self.running_account.account,)
                continue

            if timeline_pannel == 403:
                print 'Account %s is banned due to 403.' % (self.running_account.account,)
                self.ban_account(flag=403)
                self.running_account = self.get_account()
                print 'Change to Account %s.' % (self.running_account.account,)
                continue

            self.running_account.count += self.getter.access_time  # accumulate access times
            if self.running_account.count > ACCESS_LIMIT:
                self.running_account = self.update_account()
                print 'Change account to %s' % (self.running_account.account,)

            timeline_pannel = json.loads(timeline_pannel)

            try:
                errno = timeline_pannel['errno']
            except KeyError as ke:
                break
            if errno == -100:
                print 'Account %s is invalid.' % (self.running_account.account,)
                self.ban_account()
                self.running_account = self.get_account()
                print 'Change to Account %s.' % (self.running_account.account,)

        return timeline_pannel

    def fetch_timelines(self, uid):
        timeline_pannel = self.download_timelines(uid)
        timelines, otimelines, origin_users = self.parser.parse_timelines(timeline_pannel)
        timelines.extend(otimelines)
        self.profile_list.extend(origin_users)
        return timelines

    def monitor(self):
        self.running_mode = 1

        self.targets = TargetUser.get_target_users()

        self.accounts = AccountParameters.get_account_parameters(DOMAIN)
        self.running_account = self.get_account()
        print 'Account %s loaded!' % (self.running_account.account,)

        self.account_timer = Timer()

        while True:
            for tgt in self.targets:
                print 'monitor target: %s... - account %s - access count %d' % \
                      (tgt.uid, self.running_account.account, self.running_account.count)

                timelines = self.fetch_timelines(tgt.uid)
                for tmln in timelines:
                    duration = tmln.timestamp - tmln.created_at
                    days = duration.days
                    seconds = duration.seconds

                    if days != 0:
                        continue    # this post is too early.

                    if seconds < LOOP_TIME:
                        self.buffer.append(tmln)
                    else:
                        continue
                    if seconds < TIME_WINDOW:
                        self.memory.append(tmln)

                if len(self.buffer) > BUFFER_LIMIT:
                    self.reset_buffer()
                elif len(self.profile_list) > PROFILE_BUFFER_LIMIT:
                    self.reset_buffer()
                self.check_memory()

            self.reset_buffer()  # After one loop, write data to DB.

    def check_memory(self):

        new_memory = []
        for tmln in self.memory:
            now = datetime.now()
            if (now - tmln.timestamp).seconds < TIME_WINDOW:
                new_memory.append(tmln)
            else:
                continue

        self.memory = new_memory

        alarm = Alarm.get_self_alarm()
        if alarm is None:
            if len(self.memory) > THRESHOLD:
                Alarm.launch()
                self.alarm_timer = Timer()
                print 'Alarm is on!!!'
                self.memory = []
            else:
                return 0
        else:  # alarm is on
            if len(self.memory) > THRESHOLD:
                Alarm.launch()
                self.alarm_timer = Timer()
                print 'Alarmed again!!!'
                self.memory = []
            else:
                if self.alarm_timer is None:  # Ensure that the timer is not None object
                    self.alarm_timer = Timer()

                elapsed_time = self.alarm_timer.click()
                if elapsed_time.seconds > DECAY_TIME:
                    Alarm.disable()
                    print 'Alarm is off!'
                    self.alarm_timer = None
                else:
                    return 0

    def is_alarm_on(self, alarm):
        """
        To see whether the alarm is on
        :param alarm: an Alarm object
        :return: Ture if it's still on, otherwise false
        """
        if Alarm.is_it_on(alarm) is True:
            return True
        else:
            return False

    def reinforce(self):
        """
        Monitor the alarm, once it is on, it will reinforce the main spider
        If it finds the alarm is off, it will go back to his monitoring status
        :return:
        """
        self.running_mode = 2

        self.accounts = AccountParameters.get_account_parameters(DOMAIN2)
        while True:
            alarm = Alarm.get_latest_alarm()
            if alarm is None:
                print 'Waiting...'
                time.sleep(REST)
                continue

            self.running_account = self.get_account()
            self.account_timer = Timer()

            target_list = TargetUser.get_targets_by_alarm(alarm)

            while True:
                for tgt in target_list:
                    print 'Reinforce to monitor target: %s...' % (tgt.uid,)
                    timelines = self.fetch_timelines(tgt.uid)
                    self.buffer.extend(timelines)

                    if len(self.buffer) > BUFFER_LIMIT_MINI or len(self.profile_list) > PROFILE_BUFFER_LIMIT:
                        self.reset_buffer()

                self.reset_buffer()

                if self.is_alarm_on(alarm) is False:
                    print 'Alarm disabled!'
                    break
                else:
                    continue

    def get_profile(self, uid):
        timelines = self.download_timelines(uid)
        profile = self.parser.parse_profile(timelines)

        return profile

    def get_profiles(self):
        self.user_list = TargetUser.get_all_targets()
        self.accounts = AccountParameters.get_account_parameters(DOMAIN3)

        self.running_account = self.get_account()
        print 'Account %s loaded!' % (self.running_account.account,)
        self.account_timer = Timer()

        for uid in self.user_list:
            uid = str(uid)
            print 'Getting UID: %s profile...' % (uid,)

            profile = self.get_profile(uid)
            if profile is None:
                print 'No profile!!!'
                continue

            self.profile_list.append(profile)

            if len(self.profile_list) > PROFILE_LIMIT:
                User.dumps(self.profile_list)
                self.profile_list = []

        User.dumps(self.profile_list)  # clean up the bottom
        print 'All Done!'

    def get_history_posts(self, uid):
        page = 1

        while page > 0:
            if len(self.buffer) > BUFFER_LIMIT_LARGE:
                self.reset_buffer()

            print 'Getting Page %d of %s... - access count: %d' % (page, uid, self.running_account.count)
            timeline_panel = self.download_timelines(uid, page)
            timelines, otimelines = self.parser.parse_timelines(timeline_panel)

            self.buffer.extend(otimelines)

            if len(timelines) == 0:
                page = 0
                continue

            for tmln in timelines:
                if tmln.created_at < self.earliest_time:
                    page = -1  # let page equal -1 to break this loop
                else:
                    self.buffer.append(tmln)
            page += 1  # move on

    def get_history_timelines(self):
        self.running_mode = 3

        self.accounts = AccountParameters.get_account_parameters(DOMAIN3)
        self.running_account = self.get_account()
        print 'Account %s loaded!' % (self.running_account.account,)

        self.account_timer = Timer()

        for domain in xrange(MIN_DM, MAX_DM+1):
            self.targets = TargetUser.get_targets_by_domain(domain)
            i = 0
            for tgt in self.targets:
                i += 1
                print 'Getting history posts for %s - Num: %d / Domain: %d' % (tgt.uid, i, domain)
                self.get_history_posts(tgt.uid)

            self.reset_buffer()

        print 'Job Done!'














