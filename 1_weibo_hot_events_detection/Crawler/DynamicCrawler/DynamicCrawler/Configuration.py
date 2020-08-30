# coding=utf-8
VERSION = 2.0
MINUTE = 60
TIME_OUT = 30
REST = 50

######################## Crawler Config #################################

TIME_WINDOW = 10 * MINUTE   # memory 缓存时间窗口
LOOP_TIME = 70 * MINUTE    # buffer 缓存时间窗口
DECAY_TIME = 3 * TIME_WINDOW    # 警报消退时间

BUFFER_LIMIT = 300
BUFFER_LIMIT_LARGE = 3000
BUFFER_LIMIT_MINI = 600

PROFILE_BUFFER_LIMIT = 5000

PROFILE_LIMIT = 100
ACCOUNT_LIMIT = 15

TIMELINE_EARLIEST_DATETIME = '2016-1-1'  # split by '-', no zero-padding
TIMELINE_LIVE_INTERVAL = 1  # days
TIMELINE_MIGRATION_LIMIT = 5000
TIMELINE_MIGRATION_CLOCK = 1  # 1 am in the morning

####################### Resource Assignment #############################

ACCOUNT_NUM = 20  # 账号数目
DOMAIN = 0  # 常规爬虫帐号分配id, 常规爬虫任务分配id
DOMAIN2 = 11  # 支援爬虫帐号分配id
SUBDOMAIN = 1  # 支援爬虫任务分配id
DOMAIN3 = 0  # 爬取profile帐号分配id 或者 历史记录爬取帐号分配id

MIN_DM = 0
MAX_DM = 0  # 历史爬虫最小(大)任务分配id

ACCESS_LIMIT = 800  # 1小时内,单帐号访问不要超过800次.
ACCESS_TIME_WINDOW = 60 * MINUTE  # 固定为1小时, 即1小时后, 所有帐号可以reset.
THRESHOLD = 150  # 报警阈值

####################### Database ########################################
DB_USER = 'root'
DB_PASSWD = 'Lifelabmaster'  # your password

DB_DATABASE = 'Chinese_stream'
DB_HOST = '10.45.15.32' # your host address
# DB_HOST = '123.56.187.168'
DB_CHARSET = 'utf8mb4'

DB_TABLES = {
    'account_parameters': 'account_parameters',
    'target_users': 'target_users',
    'timelines': 'timelines_live',
    'alarms': 'alarms',
    'test_merge': 'test_merge',
    'users': 'users',
    'history_timelines': 'timelines_161102'
}