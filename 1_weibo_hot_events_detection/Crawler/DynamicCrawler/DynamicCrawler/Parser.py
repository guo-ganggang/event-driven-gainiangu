import json
import datetime
from Object import Timeline, Profile

def parse_origin_profile(profile):
    user = profile['user']

    dict = {
        'id': 0,
        'screen_name': '',
        'avatar': '',
        'description': '',
        'created_at': '',
        'gender': '',
        'follower_num': 0,
        'followee_num': 0,
        'weibo_num': 0,
        'level': 0,
        'location': '',
        'credit_score': 0,
        'domain': '',
        'vip_level': 0,
        'verified': 0,
        'verified_reason': '',
        'tags': '',
        'badges': '',
        'name': '',
        'json': '',
        'timestamp': datetime.datetime.now()
    }

    dict['id'] = parse_profile_id(user)
    dict['screen_name'] = parse_profile_screen_name(user)
    dict['avatar'] = parse_profile_avatar(user)
    dict['description'] = parse_profile_description(user)
    dict['created_at'] = parse_profile_created_at(user)
    dict['gender'] = parse_profile_gender(user)
    dict['follower_num'] = parse_profile_followers(user)
    dict['followee_num'] = parse_profile_followees(user)
    dict['weibo_num'] = parse_profile_weibo(user)
    dict['level'] = parse_profile_level(user)
    dict['location'] = parse_profile_location(user)
    dict['credit_score'] = parse_profile_credit_score(user)
    dict['domain'] = parse_profile_domain(user)
    dict['vip_level'] = parse_profile_vip_level(user)
    dict['verified'] = parse_profile_verified(user)
    dict['verified_reason'] = parse_profile_verified_reason(user)
    dict['tags'] = parse_profile_tags(user)
    dict['badges'] = parse_profile_badges(user)
    dict['name'] = parse_profile_name(user)

    dict['json'] = parse_profile_json(user)
    return Profile(dict)


def parse_profile(timelines):
    cards = timelines['cards']

    blog = None
    for card in cards:
        if card['card_type'] != 9:
            continue
        else:
            blog = card['mblog']
            break

    if blog is None:
        return None
    user = blog['user']

    dict = {
        'id': 0,
        'screen_name': '',
        'avatar': '',
        'description': '',
        'created_at': '',
        'gender': '',
        'follower_num': 0,
        'followee_num': 0,
        'weibo_num': 0,
        'level': 0,
        'location': '',
        'credit_score': 0,
        'domain': '',
        'vip_level': 0,
        'verified': 0,
        'verified_reason': '',
        'tags': '',
        'badges': '',
        'name': '',
        'json': '',
        'timestamp': datetime.datetime.now()
    }

    dict['id'] = parse_profile_id(user)
    dict['screen_name'] = parse_profile_screen_name(user)
    dict['avatar'] = parse_profile_avatar(user)
    dict['description'] = parse_profile_description(user)
    dict['created_at'] = parse_profile_created_at(user)
    dict['gender'] = parse_profile_gender(user)
    dict['follower_num'] = parse_profile_followers(user)
    dict['followee_num'] = parse_profile_followees(user)
    dict['weibo_num'] = parse_profile_weibo(user)
    dict['level'] = parse_profile_level(user)
    dict['location'] = parse_profile_location(user)
    dict['credit_score'] = parse_profile_credit_score(user)
    dict['domain'] = parse_profile_domain(user)
    dict['vip_level'] = parse_profile_vip_level(user)
    dict['verified'] = parse_profile_verified(user)
    dict['verified_reason'] = parse_profile_verified_reason(user)
    dict['tags'] = parse_profile_tags(user)
    dict['badges'] = parse_profile_badges(user)
    dict['name'] = parse_profile_name(user)

    dict['json'] = parse_profile_json(user)
    return Profile(dict)


def parse_profile_json(user):
    return json.dumps(user)


def parse_profile_name(user):
    return user['name']


def parse_profile_badges(user):
    badges = user['badge']
    badges_str = ''
    for key in badges:
        if badges[key] == 1:
            badges_str += key + ', '

    return badges_str.strip(', ')


def parse_profile_tags(user):
    try:
        tags = user['ability_tags']
    except KeyError as ke:
        return ''

    return tags

def parse_profile_verified_reason(user):
    return user['verified_reason']

def parse_profile_verified(user):
    return user['verified']


def parse_profile_vip_level(user):
    return user['mbrank']


def parse_profile_domain(user):
    return user['domain']


def parse_profile_credit_score(user):
    return user['credit_score']


def parse_profile_location(user):
    return user['location']


def parse_profile_level(user):
    return user['urank']


def parse_profile_weibo(user):
    return user['statuses_count']


def parse_profile_followees(user):
    return user['friends_count']


def parse_profile_followers(user):
    return user['followers_count']


def parse_profile_gender(user):
    return user['gender']


def parse_profile_created_at(user):
    created_at = user['created_at']
    return datetime.datetime.strptime(created_at, '%a %b %d %X +0800 %Y')


def parse_profile_description(user):
    return user['description']


def parse_profile_avatar(user):
    return user['avatar_hd']


def parse_profile_screen_name(user):
    return user['screen_name']


def parse_profile_id(user):
    return user['id']


def parse_timelines(timelines):
    timeline_list = []
    otimeline_list = []
    origin_user_list = []

    cards = timelines['cards']

    for card in cards:
        if card['card_type'] != 9:
            continue
        else:
            card = card['mblog']

        tmln, otmln= parse_timeline(card)
        timeline_list.append(tmln)
        if otmln is not None:
            otimeline_list.append(otmln)
            origin_user = parse_origin_profile(card['retweeted_status'])
            origin_user_list.append(origin_user)


    return timeline_list, otimeline_list, origin_user_list


def parse_timeline(timeline):
    dict = {
        'mid': '',
        'uid': '',
        'name': '',
        'omid': '',
        'ouid': '',
        'oname': '',
        'text': '',
        'app_source': '',
        'created_at': '',
        'repost_num': '',
        'favourite_num': '',
        'comment_num': '',
        'geo_info': '',
        'timestamp': datetime.datetime.now(),

        'pic_url': ''
    }

    dict['mid'] = parse_mid(timeline)
    dict['name'] = parse_name(timeline)
    dict['uid'] = parse_uid(timeline)
    dict['text'] = parse_text(timeline)
    dict['app_source'] = parse_app_source(timeline)
    dict['created_at'] = parse_created_at(timeline)
    dict['repost_num'] = parse_repost_num(timeline)
    dict['favourite_num'] = parse_favourite_num(timeline)
    dict['comment_num'] = parse_comment_num(timeline)
    dict['geo_info'] = parse_geo_info(timeline)

    dict['pic_url'] = parse_pic_urls(timeline)

    dict['omid'] = parse_omid(timeline)
    dict['ouid'] = parse_ouid(timeline)

    tmln = Timeline(dict)

    if tmln.ouid != -1 and tmln.ouid != 0:
        otmln = parse_original_timeline(timeline)
        otmln.mid = tmln.omid
        otmln.uid = tmln.ouid
        tmln.oname = otmln.name
        tmln.text = u'%s //@%s:%s' % (tmln.text, tmln.oname, otmln.text)
        tmln.pic_url = u'%s, %s' % (tmln.pic_url, otmln.pic_url)
        tmln.pic_url = tmln.pic_url.strip(u', ')
        return tmln, otmln
    else:
        return tmln, None


def parse_pic_urls(timeline):
    '''

    :param timeline:
    :return:
    '''
    pics = timeline['pic_ids']
    if len(pics) == 0:
        return u''
    else:
        pic_ids = u''
        for pic in pics:
            pic_ids += pic + u', '
        return pic_ids.strip(u', ')


def parse_name(timeline):
    return timeline['user']['name']


def parse_original_name(timeline):
    return timeline['user']['name']


def parse_original_timeline(timeline):
    dict = {
        'mid': '',
        'uid': '',
        'name': '',
        'omid': 0,
        'ouid': 0,
        'oname': '',
        'text': '',
        'app_source': '',
        'created_at': '',
        'repost_num': '',
        'favourite_num': '',
        'comment_num': '',
        'geo_info': '',
        'timestamp': datetime.datetime.now(),

        'pic_url': ''
    }
    retweet_status = timeline['retweeted_status']
    dict['name'] = parse_original_name(retweet_status)
    dict['text'] = parse_original_text(retweet_status)
    dict['app_source'] = parse_original_app_source(retweet_status)
    dict['created_at'] = parse_original_created_at(retweet_status)
    dict['repost_num'] = parse_original_reposts(retweet_status)
    dict['favourite_num'] = parse_original_favourites(retweet_status)
    dict['comment_num'] = parse_original_comments(retweet_status)
    dict['geo_info'] = parse_original_geo(retweet_status)

    dict['pic_url'] = parse_original_pic_urls(retweet_status)

    return Timeline(dict)


def parse_original_pic_urls(timeline):
    pics = timeline['pic_ids']
    if len(pics) == 0:
        return u''
    else:
        pic_ids = u''
        for pic in pics:
            pic_ids += pic + u', '
        return pic_ids.strip(u', ')


def parse_original_text(timeline):
    return timeline['text']


def parse_original_app_source(timeline):
    app = timeline['source']
    data = app.split('</a>')[0].split('>')[-1]

    return data


def parse_original_created_at(timeline):
    created_at = timeline['created_at']
    return datetime.datetime.strptime(created_at, '%a %b %d %X +0800 %Y')


def parse_original_reposts(timeline):
    return timeline['reposts_count']


def parse_original_favourites(timeline):
    return timeline['attitudes_count']


def parse_original_comments(timeline):
    return timeline['comments_count']


def parse_original_geo(timeline):
    geo = timeline['geo']
    if not isinstance(geo, dict):
        return geo

    type = geo['type']
    coordinates = geo['coordinates']
    lat = coordinates[0]
    lng = coordinates[1]

    info = 'Type: %s; Lat: %f; Lng: %f' % (type, lat, lng)

    return info


def parse_mid(timeline):
    try:
        return int(timeline['mid'])
    except Exception as e:
        print e


def parse_uid(timeline):
    try:
        return int(timeline['user']['id'])
    except Exception as e:
        print e


def parse_text(timeline):
    return timeline['text']


def parse_created_at(timeline):
    date = timeline['created_at']
    return datetime.datetime.strptime(date, '%a %b %d %X +0800 %Y')


def parse_repost_num(timeline):
    return timeline['reposts_count']


def parse_favourite_num(timeline):
    return timeline['attitudes_count']


def parse_comment_num(timeline):
    return timeline['comments_count']


def parse_app_source(timeline):
    app = timeline['source']
    data = app.split('</a>')[0].split('>')[-1]

    return data


def parse_geo_info(timeline):
    geo = timeline['geo']
    if not isinstance(geo, dict):
        return geo

    type = geo['type']
    coordinates = geo['coordinates']
    lat = coordinates[0]
    lng = coordinates[1]

    info = 'Type: %s; Lat: %f; Lng: %f' % (type, lat, lng)

    return info


def parse_omid(timeline):
    try:
        retweeted_status = timeline['retweeted_status']
    except KeyError as ke:
        return 0
    try:
        return int(retweeted_status['mid'])
    except ValueError as ve:
        return -1


def parse_ouid(timeline):
    try:
        retweeted_status = timeline['retweeted_status']
    except KeyError as ke:
        return 0

    try:
        return int(retweeted_status['user']['id'])
    except Exception as e:
        return -1  # denote that this post has been deleted.
