__author__ = 'Wei Xie'
__email__ = 'linegroup3@gmail.com'
__affiliation__ = 'Pinnacle Lab for Analytics, Singapore Management University'
__website__ = 'http://mysmu.edu/phdis2012/wei.xie.2012'


import datetime, time

import signi_processor

import fast_signi

import topic_sketch.stream as ts_stream

import exp_config

import event_output

import topic_sketch.preprocessor as preprocessor

import search

import imagecrawler

import twokenize

import tweet_stream

import user_info


_THREAD_GAP = eval(exp_config.get('detection', 'thread_gap'))

ic = imagecrawler.ImageCrawler()

class Keyword:

    def __init__(self, _word):
        self.word = _word
        self.records = list()

    def appear(self, _t, _sig):
        self.records.append((_t, _sig))

    def span(self):
        return (self.records[-1][0] - self.records[0][0]).total_seconds() / (60*60) #hours

    def print_self(self):
        print self.word + '\t' + str(self.records)


class Slice:

    def __init__(self):
        self.start = 0.0
        self.end = 0.0
        self.keywords = dict()
        self.sig = 0.0
        self.thread = []

        self.event_id = -1
        self.outputed = False

    '''
    def parse_url_from_detections(self, detections):
        ret = list()  # tweet, img, time, count

        url_candidates = set()

        records = dict()

        for detection in detections:
            t, _sig, s, tweet_item, retweet_num, comment_num = detection

            # tokenize
            try:
                tokens = twokenize.tokenizeRawTweetText(tweet_item.str)
            except:
                tokens = []

            for token in tokens:
                if token.startswith('http://t.co/') or token.startswith('https://t.co/'):
                    if not self.is_ascii(token):
                        continue
                    if token.startswith('http://t.co/'):
                        if len(token[12:]) < 3:
                            continue
                    if token.startswith('https://t.co/'):
                        if len(token[13:]) < 3:
                            continue

                    url_candidates.add(token)
                    records[token] = (tweet_item.str, tweet_item.datetime())

        for url in url_candidates:
            terms = url.split('t.co/')
            term = terms[-1]
            count = search.count(term, self.start - datetime.timedelta(hours=6), self.end + datetime.timedelta(hours=6))
            if count >= 50:
                tweet, t = records[url]
                ret.append((tweet, url, t, count))

        ret = map(lambda x: (x[0], ic.crawl(x[1]), x[2], x[3], x[1]), ret)

        ret = filter(lambda x:x[1], ret)

        return ret
    '''

    '''
    def get_representative_url(self, top_k=25):
        # return top k
        ret = list()  # tweet, img, time, count

        url_candidates = set()

        records = dict()

        for thd in reversed(self.thread):
            _ptweet = thd[-1]

            # tokenize
            try:
                tokens = twokenize.tokenizeRawTweetText(_ptweet.original_tweet.str)
            except:
                tokens = []

            for token in tokens:
                if token.startswith('http://t.co/') or token.startswith('https://t.co/'):
                    if not self.is_ascii(token):
                        continue
                    if token.startswith('http://t.co/'):
                        if len(token[12:]) < 3:
                            continue
                    if token.startswith('https://t.co/'):
                        if len(token[13:]) < 3:
                            continue

                    url_candidates.add(token)
                    records[token] = (_ptweet.original_tweet.str, _ptweet.datetime())

        for url in url_candidates:
            terms = url.split('t.co/')
            term = terms[-1]
            count = search.count(term, self.start - datetime.timedelta(hours=6), self.end + datetime.timedelta(hours=6))
            if count >= 50:
                tweet, t = records[url]
                ret.append((tweet, url, t, count))

        ret = sorted(ret, key=lambda x:x[3], reverse=True)
        ret = ret[:top_k]

        ret = sorted(ret, key=lambda x:x[2])

        ret = map(lambda x: (x[0], ic.crawl(x[1]), x[2], x[3], x[1]), ret)

        ret = filter(lambda x:x[1], ret)

        return ret
    '''

    '''
    def get_representative_tweet(self, top_k=10):
        # return top k
        ret = list()  # t, sig, s, tweet

        tweet_candidates = list()

        original_id_set = set()

        for thd in self.thread:
            t, _count, _ewma, _ewmvar, sig, s, _ptweet = thd
            tweet = _ptweet.original_tweet
            original_id = tweet.original_id()
            rt_count = tweet.retweeted_count()

            if rt_count < 25:
                continue

            if original_id not in original_id_set:
                original_id_set.add(original_id)
                tweet_candidates.append((original_id, rt_count, s, _ptweet))

        tweet_candidates = sorted(tweet_candidates, key=lambda x:x[1], reverse=True)
        tweet_candidates = tweet_candidates[:top_k]

        for tweet_candidate in tweet_candidates:
            t = tweet_candidate[3].datetime()
            sig = 0.0
            s = tweet_candidate[2]
            tweet = tweet_candidate[3].original_tweet
            rt_count = tweet_candidate[1]
            ret.append((t, sig, s, tweet, rt_count))

        return ret
    '''

    '''
    @staticmethod
    def is_ascii(s):
        return all(ord(c) < 128 for c in s)
    '''

    def summary(self):
        _current_time = time.time()

        obj = dict()

        # counting
        s = self.start
        s = s - datetime.timedelta(minutes=s.minute) - datetime.timedelta(seconds=s.second)
        s = s - datetime.timedelta(hours=6)

        e = self.end
        e = e - datetime.timedelta(minutes=e.minute) - datetime.timedelta(seconds=e.second)
        e = e + datetime.timedelta(hours=6)

        _keywords = self.ordered_keywords()[:10]

        query = ''
        for _keyword in _keywords:
            query += (_keyword + ' ')

        n_tweets, users, median, rtr, tweet_candidates, relevant_geo_tweets, images, tweet_partitions_count, original_tweets, user_details, counts_out = \
            search.explore_info_by_search(query, s, e, 1.0)
        n_users = len(users)
        obj['relevant_users'] = users
        obj['tweet_partitions_count'] = tweet_partitions_count
        obj['original_tweets'] = original_tweets
        obj['user_details'] = user_details

        if n_tweets == 0:
            return None

        # for geo tweets #############
        geo_user_set = set()

        for relevant_geo_tweet in relevant_geo_tweets:
            geo_user_set.add(relevant_geo_tweet['uid'])

        obj['relevant_geo_tweets'] = relevant_geo_tweets

        num_geo_tweets = len(relevant_geo_tweets)
        num_geo_users = len(geo_user_set)
        ##############################

        '''
        counts = list()
        counts.append((s, 0))

        count_dt = 60  # minutes
        count_multiple = 1
        try:
            while s < e:
                count = count_multiple * search.count_by_search(query, s, s + datetime.timedelta(minutes=count_dt), 1.0)
                s = s + datetime.timedelta(minutes=count_dt)
                counts.append((s, count))
        except:
            return None
        '''
        counts = counts_out

        burst = max(map(lambda x:x[1], counts))

        obj['info'] = {
            "num_tweets":n_tweets,
            "num_users":n_users,
            "num_geo_users":num_geo_users,
            "num_geo_tweets":num_geo_tweets,
            "median":median,
            "burst":burst,
            "retweetRate":rtr,
        }

        # start summary
        '''
        detections = list()  # (t, sig, set, content)
        for thd in self.thread:
            flag = False
            for id in range(len(detections)):
                if s == detections[id][2]:
                    flag = True
                    break

            if flag:
                continue

            t, _count, _ewma, _ewmvar, sig, s, _ptweet = thd

            if len(detections) > 0:
                if t - detections[-1][0] < datetime.timedelta(minutes=60):
                    if sig > detections[-1][1] :
                        detections[-1] = (t, sig, s, _ptweet.original_tweet)
                else:
                    detections.append((t, sig, s, _ptweet.original_tweet))
            else:
                detections.append((t, sig, s, _ptweet.original_tweet))
        '''
        #detections = self.get_representative_tweet()
        detections = list()
        for tweet_candidate in tweet_candidates:
            tweet_source, retweet_num, comment_num = tweet_candidate

            # tokenize
            try:
                tokens = twokenize.tokenizeRawTweetText(tweet_source['text'].lower())
            except:
                tokens = []

            tokens = map(lambda x: x.encode('utf-8'), tokens)

            print 'TOKENS:\t' + ' '.join(tokens) #  debugging
            print 'KEYWORDS:\t' + ' '.join(self.keywords.keys()) #  debugging

            s = set()
            for w in self.keywords.keys():
                w = w.encode('utf-8')
                if w in tokens:
                    s.add(w)
            print 'SET:\t' + ' '.join(s) #  debugging

            tweet_item = tweet_stream.source2tweet(tweet_source)

            t = tweet_item.datetime()

            detections.append((t, 0.0, s, tweet_item, retweet_num, comment_num))

        detections.sort(key=lambda x: x[0])

        # image
        # do not filter anything at this stage
        obj['img'] = list()
        for image in images:
            image_url = image[1]
            image_txt = image[2]["text"]
            image_t = image[2]["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            obj['img'].append([image_txt, image_url, image_t])

        #consider gap
        detections_gap = list()
        previous_t = datetime.datetime(2000,1,1)
        for detection in detections:
            if detection[0] - previous_t >= datetime.timedelta(minutes=30):
                detections_gap.append(detection)
                previous_t = detection[0]

        detections = detections_gap

        # output
        obj['tuples'] = list()

        outputs = list()
        for count in counts:
            outputs.append((count[0], count[1], None))
        for detection in detections:
            t = detection[0]
            c = estimate(t, counts)
            outputs.append((t, c, detection))

        for output in sorted(outputs, key=lambda x:x[0]):
            t = output[0]
            count = output[1]
            det = output[2]
            if det == None:
                flag = 0
                _kw = None
                txt = None
                icon = None
                uid = None
                retweet_num = None
                comment_num = None
            else:
                flag = 1
                _kw = list(det[2])
                txt = det[3].str
                txt = txt.encode('utf-8')
                retweet_num = det[4]
                comment_num = det[5]
                '''
                if det[3].is_retweet():
                    icon = tweet_user.get_user_icon(det[3].attached_obj['source_uid'])
                else:
                    icon = tweet_user.get_user_icon(det[3].attached_obj['uid'])
                '''
                uid = det[3].attached_obj['uid']
                u_obj = user_info.get_user(uid)
                if u_obj:
                    icon = u_obj['profile_image_url']
                else:
                    icon = None

            print str(t) + '\t' + str(count) + '\t' + str(txt) + '\t' + str(flag)
            obj['tuples'].append({
                "count":count,
                "tweet":txt,
                "icon":icon,
                "uid": uid,
                "keywords":_kw,
                "t":str(t),
                "present":flag,
                "retweet_num":retweet_num,
                "comment_num":comment_num,
                })

        print 'summary using ' + str(time.time() - _current_time) + 'seconds' # debugging
        return obj


    def ordered_keywords(self):
        return sorted(self.keywords, key = lambda x : self.keywords[x].span(), reverse=True)

    def output_event(self):
        try:
            _summary = self.summary()
        except:
            return

        if not _summary:
            return

        if _summary['info']['num_users'] < 50:
            print 'SUMMARY FAIL...', 'user', _summary['info']['num_users']
            print _summary
            return
        if _summary['info']['burst'] < 25:
            print 'SUMMARY FAIL...', 'burst', _summary['info']['burst']
            print _summary
            return

        if self.event_id == -1:
            self.event_id = event_output.get_event_Id()

        topic_id = event_output.get_topic_Id()

        _event = dict()

        #_event['summary'] = _summary

        _info = dict()
        _event['eid'] = self.event_id
        _event['topicID'] = topic_id
        _event['info'] = _info

        _info['dtime'] = str(self.start)
        _info['ctime'] = str(self.end)

        '''
        tweets = preprocessor.active_term_maintainer.relevant_tweets(set(self.keywords.keys()))

        users = set()
        num_rt = 0.0
        for tweet in tweets:
            users.add(tweet.uid)
            if tweet.is_retweet():
                num_rt += 1.
        '''

        tokens = list()
        for x in self.ordered_keywords():
            tokens.append(x)

        _info['keywords'] = tokens[:10]
        _info['words'] = tokens

        _summary['info']['keywords'] = tokens[:10]
        _summary['info']['words'] = tokens

        _event['summary'] = _summary

        _info['numUsers'] = _summary['info']['num_users']
        _info['numGeoUsers'] = _summary['info']['num_geo_users']
        _info['numTweets'] = _summary['info']['num_tweets']
        _info['numGeoTweets'] = _summary['info']['num_geo_tweets']
        _info['retweetRate'] = _summary['info']['retweetRate']

        _info['significance'] = self.sig
        _info['span'] = (self.end - self.start).total_seconds() / (60*60) # hours

        event_output.put(self.event_id, _event)

        #print 'put:\t' + str(_event) #debugging

    def print_self(self):
        print '[' + str(self.start) + ',' + str(self.end) + ']' + '\t' + str(self.end - self.start) + '\t' + str(self.sig) + '\t' + str(self.ordered_keywords())
        #for kw in sorted(self.keywords, key = lambda x : self.keywords[x].records[0][0]):
        for kw in sorted(self.keywords, key = lambda x : self.keywords[x].span(), reverse=True):
            self.keywords[kw].print_self()
        for th in self.thread:
            print str(th) + ':' + th[-1].original_tweet.str
        print '---------------------------------'



    def new_thread(self, sig_instance):
        _t, _count, _ewma, _ewmvar, _sig, _keywords, _ptweet = sig_instance
        self.start = _t
        self.end = _t

        for _kw in _keywords:
            _keyword = Keyword(_kw)
            _keyword.appear(_t, _sig)
            self.keywords[_kw] = _keyword

        self.thread.append(sig_instance)
        self.sig = _sig

    def get_hashtags(self, kws):
        hashtags = set(filter(lambda x: x.startswith('#'), self.keywords))
        similar_words = set()
        for ht in hashtags:
            if ht[1:] in self.keywords:
                similar_words.add(ht[1:])
        hashtags1 = hashtags.union(similar_words)

        hashtags2 = set(filter(lambda x: x.startswith('#'), kws))
        for kw in kws:
            if kw in hashtags1:
                hashtags2.add(kw)

        return hashtags1, hashtags2

    def similarity(self, sig_instance):
        _t, _count, _ewma, _ewmvar, _sig, _keywords, _ptweet = sig_instance

        if _t - self.end > datetime.timedelta(days=1):
            return 0.0

        #hashtags1 = set(filter(lambda x: x.startswith('#'), self.keywords))
        #hashtags2 = set(filter(lambda x: x.startswith('#'), _keywords))
        hashtags1, hashtags2 = self.get_hashtags(_keywords)

        if len(hashtags1.intersection(hashtags2)) < 1:
            if _t - self.end > datetime.timedelta(minutes=_THREAD_GAP):
                return 0.0

            screennames1 = set(filter(lambda x: x.startswith('@'), self.keywords))
            screennames2 = set(filter(lambda x: x.startswith('@'), _keywords))

            purewords1 = set(self.keywords.keys()) - hashtags1 - screennames1
            purewords2 = _keywords - hashtags2 - screennames2

            intersection1 = len(purewords1 & purewords2) + 0.
            if intersection1 == 0:
                return 0.0
            sim1 = intersection1 / len(purewords2)

            intersection2 = len(set(self.keywords.keys()) & _keywords) + 0.
            sim2 = intersection2 / len(_keywords)

            sim = min(sim1, sim2)

            if len(screennames1.intersection(screennames2)) >= 1:
                if intersection1 < 2:
                    return 0.0
            else:
                if intersection1 < 3:
                    return 0.0

                if sim < 0.66:
                    return 0.0

                return sim

        return len(set(self.keywords.keys()) & _keywords) + 0.

    def add_to_thread(self, sig_instance):
        _t, _count, _ewma, _ewmvar, _sig, _keywords, _ptweet = sig_instance

        if _sig > self.sig:
            self.sig = _sig

        dt = _t - self.end

        previous_len = len(self.keywords)

        self.end = _t
        self.thread.append(sig_instance)
        for _kw in _keywords:
            if _kw not in self.keywords:
                self.keywords[_kw] = Keyword(_kw)
            self.keywords[_kw].appear(_t, _sig)

        span = self.end - self.start
        if span > datetime.timedelta(minutes=5):
            if not self.outputed:
                self.output_event()
                self.outputed = True
            elif len(self.keywords) > (previous_len + 0) or dt > datetime.timedelta(hours=1):
                self.output_event()

        return True


class DetectionComponent(ts_stream.ItemStream):

    def __init__(self, _ptw_stream):
        self.ptw_stream = _ptw_stream

        _wz = eval(exp_config.get('detection', 'window_size'))
        _cycle = eval(exp_config.get('detection', 'cycle'))
        _average = eval(exp_config.get('detection', 'average'))
        print 'set signi parameters:' + str(fast_signi.SignificanceScorer.set_window_size(_wz, _cycle, _average))
        self.processor = signi_processor.SigProcessor()

        self.threads = list()

        _start_y = int(exp_config.get('detection', 'start_y'))
        _start_m = int(exp_config.get('detection', 'start_m'))
        _start_d = int(exp_config.get('detection', 'start_d'))

        self._start_t = datetime.datetime(_start_y, _start_m, _start_d)

        self.stop_tokens = {'instagram', 'facebook', 'twitter', 'update', 'pic', 'picture', 'cr', 'damn', 'hashtag'}

    def token_filter(self, tokens):
        ret = set()

        for token in tokens:
            # stop tokens
            if token in self.stop_tokens:
                continue

            # filter len <= 1
            if len(token) < 2:
                continue

            # filter time token
            try:
                datetime.datetime.strptime(token, '%y%m%d')
            except:
                ret.add(token)

        return ret

    def process(self, sig_instance):

        _t, _count, _ewma, _ewmvar, _sig, _keywords, _ptweet = sig_instance

        if _t < self._start_t:
            return 0.0

        _keywords = self.token_filter(_keywords)
        if len(_keywords) < 2:
            return 0.0
        sig_instance = _t, _count, _ewma, _ewmvar, _sig, _keywords, _ptweet

        #print 'SIGNI#\t' + str(_t) + '\t' + str(_sig) + '\t' + str(_keywords) + '\t' + _ptweet.original_tweet.str #debugging
        #return 0.0 #debugging

        create_new = True

        greatest_sim = 0.0
        host_thread = None
        for thread in reversed(self.threads):
            sim = thread.similarity(sig_instance)
            if sim > greatest_sim:
                greatest_sim = sim
                host_thread = thread

        if greatest_sim > 0.0:
            host_thread.add_to_thread(sig_instance)
            create_new = False

        if create_new:
            thread = Slice()
            thread.new_thread(sig_instance)

            self.threads.append(thread)

            return _sig

        return 0.0

    def next(self):
        ptweet = self.ptw_stream.next()

        if ptweet is ts_stream.End_Of_Stream:
            return ts_stream.End_Of_Stream

        if ptweet is None:
            return None

        sig_instance = self.processor.process(ptweet)

        if sig_instance is not None:
            output = self.process(sig_instance)

            return ptweet, output, sig_instance[-2]

        return ptweet, 0.0, None

    def print_all(self):
        #slices = sorted(self.threads, key=lambda x: x.sig, reverse=True)
        #slices = sorted(self.threads, key=lambda x: x.end - x.start, reverse=True)
        #slices = sorted(self.threads, key=lambda x: len(x.keywords), reverse=True)
        slices = sorted(self.threads, key=lambda x: x.start)
        for slice in slices:
            span = slice.end - slice.start
            if span > datetime.timedelta(minutes=5):
                #slice.print_self()
                slice.output_event()

'''
def test():
    sig_threshold = eval(exp_config.get('detection', 'signi_threshold'))
    detection_component = DetectionComponent(None)
    f = open('./sig_output.txt', 'r')
    count = 0
    for line in f:
        if line.startswith('SIGNI#'):
            terms = line.split('\t')
            _t = datetime.datetime.strptime(terms[1], '%Y-%m-%d %H:%M:%S')
            _sig = eval(terms[2])
            _keywords = eval(terms[3])
            _str = terms[4]

            if _sig < sig_threshold:
                continue

            _ptweet = ts_stream.PreprocessedTweetItem(_t, None, None, ts_stream.RawTweetItem(_t, None, _str))

            detection_component.process((_t, 0, 0, 0, _sig, _keywords, _ptweet))

            count += 1

            if (count % 100) == 0:
                print count

    detection_component.print_all()
'''

def estimate(t, seq):

    for i in range(len(seq)):
        if (t >= seq[i][0]) and (t < seq[i+1][0]):
            dt = (seq[i+1][0] - seq[i][0]).total_seconds() + 0.0
            return (seq[i+1][1] * (t - seq[i][0]).total_seconds() + seq[i][1] * (seq[i+1][0] - t).total_seconds()) / dt

'''
def summary():
    counts = list()
    f = open('../sg50_count.txt', 'r')
    for line in f:
        terms = line.split('\t')
        t = datetime.datetime.strptime(terms[0], '%Y-%m-%d %H:%M:%S')
        c = eval(terms[1])
        counts.append((t, c))

    f = open('./temp_output16.txt','r')
    threads = [] # (t, sig, set, content)
    flag = False
    for line in f:
        if line.startswith('[2015'):
            if flag:
                break
            flag = True
        if line.startswith('(datetime.'):
            terms = line.split(')')[1].split(',')
            sig = eval(terms[4])

            s_str = line.split(')')[1]
            index = s_str.index('set')
            s = eval(s_str[index:] + ')')

            index = line.index(')')
            t = eval(line[1:index + 1])

            index = line.index('>)')
            content = line[index+3: -1]

            current_thread = (t, sig, s, content)

            flag = False
            for id in range(len(threads)):
                if s == threads[id][2]:
                    if sig > threads[id][1]:
                        #threads[id] = current_thread
                        pass
                    flag = True
                    break

            if flag:
                continue

            if len(threads) > 0:
                if t - threads[-1][0] < datetime.timedelta(minutes=60):
                    if sig > threads[-1][1] :
                        threads[-1] = (t, sig, s, content)
                else:
                    threads.append((t, sig, s, content))
            else:
                threads.append((t, sig, s, content))

    for thread in threads:
        print thread

    return

    outputs = list()
    for count in counts:
        outputs.append((count[0], count[1], ''))
    for thread in threads:
        t = thread[0]
        c = estimate(t, counts)
        outputs.append((t, c, thread[3]))

    for output in sorted(outputs, key=lambda x:x[0]):
        t = output[0]
        count = output[1]
        txt = output[2]
        if txt == '':
            flag = 0
        else:
            flag = 1
        print str(t) + '\t' + str(count) + '\t' + txt + '\t' + str(flag)
'''





