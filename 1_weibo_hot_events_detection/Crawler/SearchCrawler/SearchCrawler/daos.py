import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError
from pymysql import err
from datetime import datetime, timedelta
import configs
import models

Base = declarative_base()

ENGINE_INFO = 'mysql+pymysql://' + configs.DB_USER + ':' + configs.DB_PASSWD + '@' + configs.DB_HOST \
              + '/' + configs.DB_DATABASE + '?charset=' + configs.DB_CHARSET
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


class Timeline(Base):
    __table__ = Table(configs.DB_TABLES['timelines'], Base.metadata, autoload=True, autoload_with=ENGINE)

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
                timeline = Timeline(tmln)
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


class Account(Base):
    __table__ = Table(configs.DB_TABLES['accounts'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, acct):
        l = acct.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def get_accounts(cls):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.cid == configs.CRAWLER_ID).limit(configs.ACC_MAX_NUM)
        for c in cursor:
            results.append(models.Account(
                    s=c.s, gsid=c.gsid, cid=c.cid,
                    username=c.username, password=c.password
                )
            )

        db.close()

        print 'Get %d accounts for Crawler %d...' % (len(results), configs.CRAWLER_ID)
        return results


class Keyword(Base):
    __table__ = Table(configs.DB_TABLES['keywords'], Base.metadata, autoload=True, autoload_with=ENGINE)

    def __init__(self, keywd):
        l = keywd.__dict__
        for key, value in l.items():
            setattr(self, key, value)

    @classmethod
    def get_keywords(cls):
        db = Database()
        db.connect()

        results = []
        cursor = db.session.query(cls).filter(cls.cid == configs.CRAWLER_ID).all()
        for c in cursor:
            results.append(
                models.Keyword(
                    keyword=c.keyword,
                    cid=c.cid,
                    score=c.score,
                    timestamp=c.timestamp
                )
            )

        db.close()

        print 'Get %d keywords as Crawler %d' % (len(results), configs.CRAWLER_ID)
        results.sort(key=lambda x: -x.score)
        return results

    @classmethod
    def dump_keywords(cls, keywords):
        db = Database()
        db.connect()

        for keyword in keywords:
            db.session.merge(cls(keyword))

        db.close()

    @classmethod
    def disable_keywords(cls, keywords):
        """

        :param keywords: a list of Keyword Objects in models.py
        :return:
        """
        print 'There are %d keywords in total!' % (len(keywords),)
        disabled_num = 0
        db = Database()
        db.connect()

        now = datetime.now()

        for keyword in keywords:
            result = db.session.query(cls).filter(cls.keyword == keyword.keyword).one()
            timestamp = result.timestamp
            if(timestamp + timedelta(days=configs.MONITOR_TIME_SPAN) < now):
                result.cid = -1
                disabled_num += 1

        db.close()
        print '%d keywords have been disabled!' % (disabled_num,)

