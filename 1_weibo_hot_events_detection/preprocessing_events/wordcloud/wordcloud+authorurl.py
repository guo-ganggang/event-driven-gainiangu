import time

from datetime import datetime, date, timedelta as td

import pymysql
import redis
import json
import jieba
import codecs

_KEY_EVENT_CHANNEL = 'twitter:sg:event:python:weibo:ab_test:a'
_KEY_EVENT_PREFIX = _KEY_EVENT_CHANNEL + ':'
_KEY_EVENT_KEYWORDS = _KEY_EVENT_PREFIX + 'keywords'
_KEY_EVENT_KEYWORDS_TRACK2 = _KEY_EVENT_PREFIX + 'track2'
_KEY_EVENT_KEYWORDS_WORDCLOUD = _KEY_EVENT_PREFIX + 'wordcloud'

class Cloud:

    def __init__(self):

        # self.start = start
        #
        # self.end = end

        self.delta = td(seconds=10)

        self.lag = td(minutes=2 * 60 + 30)

        self.host = '10.0.109.33'
        self.user = 'clear'
        self.db = 'clear'
        self.charset = 'utf8'

        self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset, passwd='ClearDataBase2017^')

    def currentid(self):
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            nextid = db.get(_KEY_EVENT_PREFIX + 'nextId')
            id = int(nextid)
        except:
            print('redis connection failure')
        return id

    def info(self,id):
        kws =[]
        obj={}
        print(id)
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            content = db.get(_KEY_EVENT_PREFIX + str(id)).decode('utf-8')
            dic = json.loads(content)
            obj['kws'] = dic['info']['words']
            obj['tm1']= dic['summary']['tweet_partitions_count']['timestamps'][0]
            obj['tm2'] = dic['summary']['tweet_partitions_count']['timestamps'][-1]
            obj['id'] = id
            obj['timestamps']= dic['summary']['tweet_partitions_count']['timestamps']
            obj['counts'] = dic['summary']['tweet_partitions_count']['counts']
            obj['tweets']=dic ['summary']['original_tweets']

        # kws.append(tm1)
        # kws.append(tm2)
        # print('kws etc',obj)
        except:
            print('redis connection failure')
            db = redis.StrictRedis('10.0.109.33', port=8181)
            content = db.get(_KEY_EVENT_PREFIX + str(id)).decode('utf-8')
            dic = json.loads(content)
            obj['kws'] = dic['info']['words']
            obj['tm1']= dic['summary']['tweet_partitions_count']['timestamps'][0]
            obj['tm2'] = dic['summary']['tweet_partitions_count']['timestamps'][-1]
            obj['id'] = id
            obj['timestamps']= dic['summary']['tweet_partitions_count']['timestamps']
            obj['counts'] = dic['summary']['tweet_partitions_count']['counts']
            obj['tweets']=dic ['summary']['original_tweets']
        return obj

    def topkauthor(self,id,k):
        timestamps = self.info(id)['timestamps']
        counts = self.info(id)['counts']
        tweets = self.info(id)['tweets']
        rankdict = {}
        for item in counts:
            rankdict[item]= sum(counts[item])
        ranksorted = sorted(rankdict.items(), key=lambda x: x[1], reverse=True)
        topk = ranksorted[0:k]
        print(topk)
        print(type(topk))
        print(len(topk))
        authors=[]
        for ak in range(min(k,len(topk))):
            tweet = topk[ak][0]
            if topk[ak][1]>1:
            # if (tweet in tweets):
                authors.append(str(tweets[tweet][2]))
        print(authors)
        return authors

    def getauthorsinfo(self,authors):
        try:
            conn = pymysql.connect(host='123.56.187.168', user='zhouying', db='Chinese_stream', charset='utf8',
                                   passwd='Yingzhou765')

            cursor = conn.cursor()
            print(','.join(authors))
            sql_txt = 'select * from users where id in ('+ ','.join(authors) +')'
            print(sql_txt)
            cursor.execute(sql_txt)
            ret = cursor.fetchall()
        except:
            time.sleep(900)
            conn = pymysql.connect(host='123.56.187.168', user='zhouying', db='Chinese_stream', charset='utf8',
                                   passwd='Yingzhou765')

            cursor = conn.cursor()
            print(','.join(authors))
            sql_txt = 'select * from users where id in ('+ ','.join(authors) +')'
            print(sql_txt)
            cursor.execute(sql_txt)
            ret = cursor.fetchall()
        finally:
            # print res
            cursor.close()
            conn.close()
        return ret

    def insertauthorsinfo(self,ret):
            conn = pymysql.connect(host='10.0.109.33', user='clear', db='clear', charset='utf8', passwd='ClearDataBase2017^')
            cursor = conn.cursor()
            for row in ret:
                ls = list(row)
                ls[3]=ls[3].replace('\'','')
                ls[-2]=ls[-2].replace('\'','')
                newrow = tuple(ls)
                sql_insert = "replace into users_all values('%d','%s','%s','%s','%s','%s','%d','%d','%d','%d','%s','%d','%s','%d','%d','%s','%s','%s','%s','%s','%s')" % newrow
                # print(sql_insert)
                cursor.execute(sql_insert)
                conn.commit()
            cursor.close()
            conn.close()

    def relatedwb(self,id):
        ret = []
        # try:
        print('closing old connection...')
        self.connection.close()
        print('sleep 2 seconds')
        time.sleep(2)
        kw = self.info(id)['kws']
        t0 = self.info(id)['tm1']
        t1 = self.info(id)['tm2']
        print(kw)
        print(type(kw))
        str = '(instr(text,\''+ kw[0]+'\')>0)'
        # print(str)
        for k in range(1,len(kw)):
            app = '+(instr(text,\''+ kw[k]+'\')>0)'
            str += app
        print(str)
        sqlstr = 'SELECT text FROM clear.timelines2 where' + str + '>1 and created_at >\'' +t0 +'\' and created_at <\'' +t1 +'\''
        print(sqlstr)
        print('trying to reconnect db...')
        try:
            self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset,
                                              passwd='ClearDataBase2017^')
            print('successful connection!')
            cursor = self.connection.cursor()
            cursor.execute(sqlstr)
            ret = cursor.fetchall()
            print(len(ret))
            cursor.close()
        except:
            self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset,
                                              passwd='ClearDataBase2017^')
            print('successful connection!')
            cursor = self.connection.cursor()
            cursor.execute(sqlstr)
            ret = cursor.fetchall()
            print(len(ret))
            cursor.close()
        return ret

    def getString(self, tweets, stopwords):
            txtstr = ''
            for row in tweets:
                tweet = row[0]
                try:
                    txt = tweet.split(':')[1].replace('http', '').replace('\n', ' ')
                except:
                    txt = tweet

                txtstr = txtstr + ' ' + txt

            worddict = cloud.count(txtstr, stopwords)
            return worddict


    def stopword(self, filename):#delete stopword
        stopwords = set()
        with codecs.open(filename, 'r' ,'utf-8') as f:
            for line in f:
                stopwords.add(line.rstrip())
        # # f = open(filename, 'r')
        # line = f.readline().rstrip()
        # while line:
        #     # stopwords.setdefault(line, 0)
        #     # print(line)
        #     stopwords.add(line)
        #     line = f.readline().rstrip()
        # f.close()
        return stopwords


    def count(self, txtstr, stopwords):
        seg_generator = jieba.cut(txtstr)  # split word
        print(seg_generator)
        seg_list = [i for i in seg_generator if i not in stopwords]
        seg_list = [i for i in seg_list if i != u' ']
        seg_list = r' '.join(seg_list)

        worddict = {}
        wordlist = seg_list.split(' ')
        for word in wordlist:  # calculate word count
            #     print word
            # word = word.encode('utf-8')
            if word not in worddict:
                worddict[word] = 1
            else:
                worddict[word] = worddict[word] + 1

        return worddict



    def analysis(self,id,n):
        # cloud = Cloud()
        stopwords = self.stopword('stopwords.txt')
        res = self.relatedwb(id)
        worddict = self.getString(res, stopwords)
        worddict["\u200b"]=0
        dictlist = sorted(worddict.items(), key=lambda x: x[1], reverse=True)
        maxcount = dictlist[0][1]
        # print(dictlist)
        result = dictlist[0: n]
        finallist = {}
        count_key = 0
        for k,v in dictlist:
            v = v*40.0/maxcount
            if v>=10:
                finallist[k]=v
                count_key += 1
        #finalsort = sorted(finallist.items(), key=lambda x: x[1], reverse=True)

        # print('result:',result[0])
        # print('finaldict',finallist)
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            json_obj = json.dumps(finallist)
            cloudkey = _KEY_EVENT_KEYWORDS_WORDCLOUD + ':'+str(id)
            db.set(cloudkey, json_obj)
            print(db.get(cloudkey))
        except:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            json_obj = json.dumps(finallist)
            cloudkey = _KEY_EVENT_KEYWORDS_WORDCLOUD + ':'+str(id)
            db.set(cloudkey, json_obj)
            print(db.get(cloudkey))
        #return result


if __name__ == "__main__":
    cloud=Cloud()
    n=15
    # for id in range(currentid - 5, currentid + 1):
    #     authors = cloud.topkauthor(id, 4)
    #     ainfo = cloud.getauthorsinfo(authors)
    #     cloud.insertauthorsinfo(ainfo)
    #     print time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # print 'finish'

    while True:
        currentid = cloud.currentid()
        print('current id is: %s' % (currentid))
        # for id in range(currentid-5, currentid+1):
        for id in range(currentid-40, currentid+1):
            cloud.analysis(id,n)
            authors = cloud.topkauthor(id, 4)
            if (authors==[]):
                print('eid',id,'no author,skip')
            else:
                ainfo = cloud.getauthorsinfo(authors)
                cloud.insertauthorsinfo(ainfo)
                print(time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time())))
                print('eid',id,'done')

        print("finish,sleep 15 min")
        time.sleep(900)
