from Configuration import TIMELINE_LIVE_INTERVAL, TIMELINE_MIGRATION_CLOCK
from datetime import datetime, timedelta
import time
from Database import Timelines, HistotyTimelines


def migrate_timelines():
    now = datetime.now()
    history = now - timedelta(days=TIMELINE_LIVE_INTERVAL)
    print 'Now is ' + now.__str__()
    print 'History is ' + history.__str__()

    tm_num = 0
    while True:
        timelines = Timelines.migrate(history)
        if len(timelines) == 0:
            break
        else:
            HistotyTimelines.dump(timelines)
            Timelines.delete_all(timelines)
            print 'Migrate %d timelines...' % (len(timelines),)
            tm_num += len(timelines)

    print 'Totally migrate %d timelines...' % (tm_num,)

if __name__ == '__main__':

    while True:
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        schedule = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                            hour=TIMELINE_MIGRATION_CLOCK, minute=tomorrow.minute, microsecond=tomorrow.microsecond, second=tomorrow.second)

        sleep_time = (schedule - now).seconds
        print "It's going to sleep %d seconds..." % (sleep_time,)
        time.sleep(sleep_time)
        migrate_timelines()
        time.sleep(3600)  # Sleep one hour