import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
import Configuration
import Object
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from pymysql import err

Base = declarative_base()

ENGINE_INFO = 'mysql+pymysql://' + Configuration.DB_USER + ':' + Configuration.DB_PASSWD + '@' + Configuration.DB_HOST \
              + '/' + Configuration.DB_DATABASE + '?charset=' + Configuration.DB_CHARSET
ENGINE = sqlalchemy.create_engine(ENGINE_INFO)


class Database(object):
    def __init__(self):
        self.engine = ENGINE
        self.connection = None
        self.session = None

    def connect(self):
        self.connection = self.engine.connect()
        session = sessionmaker(bind=self.engine, autocommit=False)
        self.session = session()

    def close(self):
        try:
            self.session.commit()
        except err.InternalError as eie:
            print eie
            self.session.rollback()
            return -1
        except IntegrityError as ie:
            print ie
            self.session.rollback()
            return -1

        self.session.close()
        self.connection.close()
        return 0


class AccountParameters(Base):
    __table__ = Table(Configuration.DB_TABLES['account_parameters'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, accs):
        l = accs.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def supplement_account(cls, domain):
        db = Database()
        db.connect()

        remain_num = len(
            db.session.query(cls).filter(cls.domain == domain).all()
        )
        supplement_num = Configuration.ACCOUNT_NUM - remain_num

        cursor = db.session.query(cls).filter(cls.domain == 0).limit(supplement_num)
        for c in cursor:
            c.domain = domain

        db.close()

        print 'Supplement %d accounts in Domain %d!!!' % (supplement_num, domain)

        return 0


    @classmethod
    def reset403(cls):
        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.domain == 403).all()
        for c in cursor:
            c.domain = 0

        db.close()

        print 'Reset all 403 accounts to be available.'

        return 0


    @classmethod
    def add_accounts(cls, accounts):
        """

        :param accounts: A list of Account(Object.py) objects
        :return:
        """
        db = Database()
        db.connect()

        for acc in accounts:
            try:
                db.session.add(AccountParameters(acc))
                db.session.commit()
            except IntegrityError as ie:
                print ie
                db.session.rollback()
                continue

        db.session.close()
        db.connection.close()

    @classmethod
    def ban(cls, account, flag):
        """
        Ban account specified by account
        :return:
        """
        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.account == account.account).one()
        if flag == -1:
            cursor.domain = -account.domain
        else:
            cursor.domain = flag

        db.close()



    @classmethod
    def get_account_parameters(cls, domain):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.domain == domain).limit(Configuration.ACCOUNT_NUM)
        for c in cursor:
            results.append(Object.AccountParameters(i=c.i, s=c.s, gsid=c.gsid, domain=c.domain, account=c.account))

        db.close()

        print 'Get %d Domain %d accounts...' % (len(results), domain)
        return results


class TargetUser(Base):
    __table__ = Table(Configuration.DB_TABLES['target_users'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, l):
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def get_all_targets(cls):
        """

        :return: only uid
        """
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).all()

        for c in cursor:
            results.append(c.uid)
        db.close()

        print 'Get %d target uid!!!' % (len(results),)
        return results

    @classmethod
    def get_targets_by_alarm(cls, alarm):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.domain == alarm.domain
                                              and cls.subdomain == Configuration.SUBDOMAIN).all()

        for c in cursor:
            results.append(
                Object.TargetUser(c.uid, c.weight, c.domain, c.subdomain)
            )

        db.close()

        print 'Get %d targets from Domain %d Subdomain %d' % (len(results), alarm.domain, Configuration.SUBDOMAIN)
        return results

    @classmethod
    def get_targets_by_domain(cls, domain):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.domain == domain).all()
        for c in cursor:
            results.append(
                Object.TargetUser(c.uid, c.weight, c.domain, c.subdomain)
            )

        db.close()

        print 'Get %d targets of Domain %d!!!' % (len(results), domain)
        return results

    @classmethod
    def get_target_users(cls):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.domain == Configuration.DOMAIN).all()
        for c in cursor:
            results.append(
                Object.TargetUser(c.uid, c.weight, c.domain, c.subdomain)
            )

        db.close()

        print 'Get %d target users, specified by ""DOMAIN: %d"' % (len(results), Configuration.DOMAIN)
        return results


class Timelines(Base):
    __table__ = Table(Configuration.DB_TABLES['timelines'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, tmln):
        l = tmln.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def dump(cls, timeline_list):
        mid_list = []
        timelines = []
        for tmln in timeline_list:
            if tmln.mid not in mid_list:
                mid_list.append(tmln.mid)
                timelines.append(tmln)
            else:
                continue

        timelines.sort(key=lambda x: x.mid)  # sort the timelines to prevent the deadlock

        db = Database()
        db.connect()

        while True:
            flag = 0
            for tmln in timelines:
                timeline = Timelines(tmln)
                try:
                    db.session.merge(timeline)
                except err.InternalError as eie:
                    db.session.rollback()
                    flag = 1
                    break
                except IntegrityError as ie:
                    db.session.rollback()
                    flag = 1
                    break
            if flag == 1:
                continue

            retcode = db.close()
            if retcode == 0:
                break

    @classmethod
    def migrate(cls, timestamp):
        db = Database()
        db.connect()

        results = db.session.query(cls).filter(cls.created_at < timestamp).limit(Configuration.TIMELINE_MIGRATION_LIMIT).all()
        if len(results) == 0:
            db.close()
            return []

        timelines = []
        for tmln in results:
            timelines.append(Object.Timeline(tmln.__dict__))

        db.close()
        return timelines

    @classmethod
    def delete_all(cls, timelines):
        db = Database()
        db.connect()

        for tmln in timelines:
            db.session.query(cls).filter(cls.mid == tmln.mid).delete()

        db.close()


class User(Base):
    __table__ = Table(Configuration.DB_TABLES['users'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, user):
        l = user.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def dumps(cls, user_list):
        db = Database()
        db.connect()

        uid_list = []
        users = []
        for user in user_list:
            if user.id not in uid_list:
                uid_list.append(user.id)
                users.append(user)

        users.sort(key=lambda x: x.id)  # sort the timelines to prevent the deadlock

        while True:
            flag = 0
            for user in users:
                try:
                    db.session.merge(User(user))
                except IntegrityError as ie:
                    print ie
                    db.session.rollback()
                    flag = 1
                    break
            if flag != 0:
                continue

            retcode = db.close()
            if retcode == 0:
                break

        print '%d users are dumped into DB!!!' % (len(user_list),)
        return 0


class Alarm(Base):
    __table__ = Table(Configuration.DB_TABLES['alarms'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, alarm):
        l = alarm.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def launch(cls):
        '''
        Lauch an alarm with domain id 'DOMAIN'
        :return:
        '''
        db = Database()
        db.connect()

        db.session.merge(Alarm(Object.Alarm(Configuration.DOMAIN)))

        db.close()

    @classmethod
    def disable(cls):
        """
        Disable the alarm of the this spider
        :return:
        """
        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.domain == Configuration.DOMAIN).one()

        cursor.is_on = 0

        db.close()

    @classmethod
    def get_self_alarm(cls):
        db = Database()
        db.connect()

        alarm = None
        try:
            cursor = db.session.query(cls).filter(cls.domain == Configuration.DOMAIN).one()
        except Exception as e:
            db.close()
            return alarm

        if cursor.is_on == 0:
            db.close()
            return alarm
        else:
            alarm = Object.Alarm(
                domain=cursor.domain,
                is_on=cursor.is_on,
                launch_time=cursor.launch_time
            )
            db.close()
            return alarm


    @classmethod
    def get_latest_alarm(cls):
        """
        Get the latest alarm
        :return: Alarm object in Object.py
        """
        db = Database()
        db.connect()

        alarm = None
        earliest = datetime.now()

        cursor = db.session.query(cls).filter(cls.is_on == 1).all()

        if len(cursor) == 0:
            db.close()
            return alarm  # at this point the alarm must be None
        else:
            for c in cursor:
                if c.launch_time < earliest:
                    alarm = c
                    earliest = c.launch_time

            alarm = Object.Alarm(
                domain=alarm.domain,
                is_on=alarm.is_on,
                launch_time=alarm.launch_time
            )
            db.close()
            return alarm

    @classmethod
    def is_it_on(cls, alarm):
        """
        To check the alarm whether is on in DB
        :param alarm: Alarm object in Object.py
        :return:
        """

        db = Database()
        db.connect()

        cursor = db.session.query(cls).filter(cls.domain == alarm.domain).one()

        if cursor.is_on == 1:
            db.close()
            return True
        else:
            db.close()
            return False


class TestMerge(Base):
    __table__ = Table(Configuration.DB_TABLES['test_merge'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, test_merge):
        l = test_merge.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def insert_items(cls, item_list):
        db = Database()
        db.connect()
        while True:
            for item in item_list:
                item = TestMerge(item)
                db.session.merge(item)

            retcode = db.close()
            if retcode == 0:
                break


class HistotyTimelines(Base):
    __table__ = Table(Configuration.DB_TABLES['history_timelines'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, tmln):
        l = tmln.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def dump(cls, timeline_list):
        mid_list = []
        timelines = []
        for tmln in timeline_list:
            if tmln.mid not in mid_list:
                mid_list.append(tmln.mid)
                timelines.append(tmln)
            else:
                continue

        timelines.sort(key=lambda x: x.mid)  # sort the timelines to prevent the deadlock

        db = Database()
        db.connect()

        while True:
            flag = 0
            for tmln in timelines:
                timeline = HistotyTimelines(tmln)
                try:
                    db.session.merge(timeline)
                except err.InternalError as eie:
                    db.session.rollback()
                    flag = 1
                    break
                except IntegrityError as ie:
                    db.session.rollback()
                    flag = 1
                    break
            if flag == 1:
                continue

            retcode = db.close()
            if retcode == 0:
                break













