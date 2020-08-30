__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import numpy as np
import MySQLdb
import twokenize
from timeout import timeout
import exp_config
import copy
import datetime
import user_info

### configuration ########
_host = exp_config.get('database', 'host')
_user = exp_config.get('database', 'user')
_db = exp_config.get('database', 'db')
_charset = exp_config.get('database', 'charset')

### for id mapping #########
_connection = MySQLdb.connect(host=_host, user=_user, passwd='123456', db=_db, charset=_charset)

_cursor = _connection.cursor()
_cursor.execute("desc timelines2")
_id = 0
_id_map = {}
for column in _cursor.fetchall():
    _id_map[column[0]] = _id
    _id += 1
###########################################


def relative_score1(keywords, txt):
    tokens = twokenize.tokenizeRawTweetText(txt)

    score = 0.0

    for token in tokens:
        if token in keywords:
            score += 1

    score /= 3
    return score


def relative_score2(keywords, txt):
    tokens = twokenize.tokenizeRawTweetText(txt)

    words = set()

    for token in tokens:
        if token in keywords:
            words.add(token)

    score = len(words)
    score /= 2
    return score


def relative_score(keywords, txt):
    return min(relative_score1(keywords, txt), relative_score2(keywords, txt))


@timeout(60*30)
def count(query, t_start, t_end):
    connection = MySQLdb.connect(host=_host, user=_user, passwd='123456', db=_db, charset=_charset)
    cursor = connection.cursor()
    sql_str = 'select count(*) from timelines2 where created_at >= "' + str(t_start) + '" and created_at < "' \
              + str(t_end) + '" and text like "%' + query + '%"'

    cursor.execute(sql_str)

    row = cursor.fetchone()
    return row[0]


@timeout(60*30)
def count_by_search(query, t_start, t_end, min_score=0.0):
    connection = MySQLdb.connect(host=_host, user=_user, passwd='123456', db=_db, charset=_charset)
    cursor = connection.cursor()
    sql_str = 'select text from timelines2 where created_at >= "' + str(t_start) + '" and created_at < "' \
              + str(t_end) + '"'
    print sql_str
    cursor.execute(sql_str)

    count = 0
    keywords = set(query.split(' '))

    row = cursor.fetchone()
    while row:
        txt = row[0]

        score = relative_score(keywords, txt)

        if score >= min_score:
            count += 1

        row = cursor.fetchone()

    return count


def count_user_by_search(query, t_start, t_end, min_score=0.0):
    return 0


def count_info_by_search(query, t_start, t_end, min_score=0.0):
    return 0, 0, 0, 0


def get_real_source_mid(tree_map, mid):
    search_id = mid
    while search_id in tree_map:
        print 'in tree...'
        search_id = tree_map[search_id]

    return search_id


def get_source_tweet(txt):
    index = txt.rfind('//@')
    return txt[index:]


@timeout(60*30)
def explore_info_by_search(query, t_start, t_end, min_score=0.0):
    print 'entering explore_info'

    connection = MySQLdb.connect(host=_host, user=_user, passwd='123456', db=_db, charset=_charset)
    cursor = connection.cursor()
    sql_str = 'select * from timelines2 where created_at >= "' + str(t_start) + '" and created_at < "' \
              + str(t_end) + '"'
    print sql_str
    cursor.execute(sql_str)

    tweet_partitions = dict()
    tree_map = dict()
    original_tweets = dict()
    users = dict()
    user_details = dict()
    tweet_candidates = list()
    images = list()
    relevant_geo_tweets = list()

    n_tweets = 0
    n_retweets = 0
    keywords = set(query.split(' '))

    row = cursor.fetchone()
    while row:
        _obj = {
            "mid" : row[_id_map["mid"]],
            "uid" : row[_id_map["uid"]],
            "created_at" : row[_id_map["created_at"]],
            "text" : row[_id_map["text"]],
            "source_mid" : row[_id_map["omid"]],
            "source_uid" : row[_id_map["ouid"]],
            "retweet_num" : row[_id_map["repost_num"]],
            "comment_num" : row[_id_map["comment_num"]],
            "pic_url" : row[_id_map["pic_url"]],
            "geo_info" : row[_id_map["geo_info"]]
        }

        txt = _obj["text"]

        score = relative_score(keywords, txt)

        if score < min_score:
            row = cursor.fetchone()
            continue

        n_tweets += 1

        uid = _obj["uid"]
        mid = _obj["mid"]
        source_mid = _obj["source_mid"]
        source_uid = _obj["source_uid"]

        retweet_num = _obj["retweet_num"]
        comment_num = _obj["comment_num"]

        if len(_obj["pic_url"]) > 0:
            img_str = _obj["pic_url"]
            imgs = img_str.split(",")
            for img in imgs:
                img_url = 'http://ww3.sinaimg.cn/large/' + img + '.jpg'
                images.append((retweet_num + comment_num, img_url, _obj))
                break

        if len(_obj["geo_info"]) > 0:
            print 'HAS_GEO_TWEETS!'
            geo_obj = copy.copy(_obj)
            geo_obj['created_at'] = geo_obj['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            relevant_geo_tweets.append(geo_obj)

        tweet_candidates.append((_obj, retweet_num, comment_num))

        if source_mid:
            n_retweets += 1

            original_tweets[source_mid] = [get_source_tweet(txt), source_mid, source_uid, mid, uid]

            tree_map[mid] = source_mid
            real_source_mid = get_real_source_mid(tree_map, source_mid)

            source_mid = real_source_mid
            if source_mid not in tweet_partitions:
                tweet_partitions[source_mid] = list()
            tweet_partitions[source_mid].append((mid, _obj['created_at']))
        else:
            if mid not in tweet_partitions:
                tweet_partitions[mid] = list()
            tweet_partitions[mid].append((mid, _obj['created_at']))

        if uid in users:
            users[uid] += 1
        else:
            users[uid] = 1

        row = cursor.fetchone()

    if n_tweets > 0:
        rtr = n_retweets / n_tweets
    else:
        rtr = 0.0

    tweet_candidates = sorted(tweet_candidates, key=lambda x: x[1] + x[2], reverse=True)[:5]

    images.sort(reverse=True)
    images = images[:10]

    # user details
    for uid in users:
        user_details[uid] = user_info.get_user(uid)

    # count tweet for each partition
    tweet_partitions_count = dict()
    tweet_partitions_timestamps = list()
    tweet_partitions_timestamps_ = list()
    s = t_start
    e = t_end
    count_dt = 60  # minutes
    tweet_partitions_timestamps.append(str(s))
    tweet_partitions_timestamps_.append(s)
    while s < e:
        s = s + datetime.timedelta(minutes=count_dt)
        tweet_partitions_timestamps.append(str(s))
        tweet_partitions_timestamps_.append(s)

    for omid in tweet_partitions:

        s = t_start
        e = t_end

        tweets = tweet_partitions[omid]

        tweet_partitions_count[omid] = list()
        tweet_partitions_count[omid].append(0)

        count_dt = 60  # minutes
        count_multiple = 1
        while s < e:
            count = 0
            current_e = s + datetime.timedelta(minutes=count_dt)

            for mid, t in tweets:
                if t >= s:
                    if t < current_e:
                        count += 1
                    else:
                        break

            count *= count_multiple
            s = s + datetime.timedelta(minutes=count_dt)
            tweet_partitions_count[omid].append(count)

    total_counts = 0

    for omid in tweet_partitions_count:
        total_counts += np.array(tweet_partitions_count[omid])

    counts_out = zip(tweet_partitions_timestamps_, total_counts.tolist())

    tweet_partitions_count_out = {'timestamps': tweet_partitions_timestamps, 'counts': tweet_partitions_count}
    return n_tweets, users, np.median(users.values()), rtr, tweet_candidates, relevant_geo_tweets, \
           images, tweet_partitions_count_out, original_tweets, user_details, counts_out


def search(query, t_start, t_end):
    return []


def range(t_start, t_end):
    return []