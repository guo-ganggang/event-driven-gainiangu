import time

from datetime import datetime, date, timedelta as td

import pymysql
import redis
import json
import jieba

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

        self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset, passwd='clear')
        # cursor = self.connection.cursor()
        # cursor.execute("desc timelines2")
        # id = 0
        # self.id_map = {}
        # for column in cursor.fetchall():
        #     self.id_map[column[0]] = id
        #     id += 1
        # cursor.close()

    def currentid(self):
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            nextid = db.get(_KEY_EVENT_PREFIX + 'nextId')
            id = int(nextid)
        except:
            print 'redis connection failure'
        return id

    def info(self,id):
        kws =[]
        obj={}
        print id
        try:
            db = redis.StrictRedis('10.0.109.33', port=8181)
            content = db.get(_KEY_EVENT_PREFIX + str(id))
            dic = json.loads(content)
            obj['kws'] = dic['info']['words']
            obj['tm1']= dic['summary']['tweet_partitions_count']['timestamps'][0]
            obj['tm2'] = dic['summary']['tweet_partitions_count']['timestamps'][-1]
            obj['id'] = id
            # kws.append(tm1)
            # kws.append(tm2)
            print 'kws etc',obj
        except:
            print 'redis connection failure'

        return obj

    def relatedwb(self,id):
        ret = []
        try:
            print 'closing old connection...'
            self.connection.close()
            print 'sleep 2 seconds'
            time.sleep(2)
            kw = self.info(id)['kws']
            t0 = self.info(id)['tm1']
            t1 = self.info(id)['tm2']
            print kw
            print type(kw)
            str = '(instr(text,\''+ kw[0]+'\')>0)'
            print str
            for k in range(1,len(kw)):
                app = '+(instr(text,\''+ kw[k]+'\')>0)'
                str += app
            print str
            sqlstr = 'SELECT text FROM clear.timelines2 where' + str + '>1 and created_at >\'' +t0 +'\' and created_at <\'' +t1 +'\''
            print sqlstr
            print 'trying to reconnect db...'
            self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db, charset=self.charset,
                                              passwd='clear')
            print 'successful connection!'
            cursor = self.connection.cursor()
            cursor.execute(sqlstr)
            ret = cursor.fetchall()
            print len(ret)
            cursor.close()
        except:
            print 'mysqlconnection failure'
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
        stopwords = {}
        f = open(filename, 'r')
        line = f.readline().rstrip()
        while line:
            stopwords.setdefault(line, 0)
            stopwords[line.decode('utf-8')] = 1
            line = f.readline().rstrip()
        f.close()
        return stopwords


    def count(self, txtstr, stopwords):
        seg_generator = jieba.cut(txtstr)  # split word
        seg_list = [i for i in seg_generator if i not in stopwords]
        seg_list = [i for i in seg_list if i != u' ']
        seg_list = r' '.join(seg_list)

        worddict = {}
        wordlist = seg_list.split(' ')
        for word in wordlist:  # calculate word count
            #     print word
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
        dictlist = sorted(worddict.items(), key=lambda x: x[1], reverse=True)
        maxcount = dictlist[0][1]
        result = dictlist.__getslice__(0, n)
        finallist = {}
        for k,v in dictlist:
            v = v*40.0/maxcount
            if v>=10:
                finallist[k]=v
        #finalsort = sorted(finallist.items(), key=lambda x: x[1], reverse=True)

        print 'result:',result
        print 'finaldict',finallist
        db = redis.StrictRedis('10.0.109.33', port=8181)
        json_obj = json.dumps(finallist)
        cloudkey = _KEY_EVENT_KEYWORDS_WORDCLOUD + ':'+str(id)
        db.set(cloudkey, json_obj)
        print db.get(cloudkey)
        #return result


if __name__ == "__main__":
    cloud=Cloud()
    n=15
    while True:
        currentid = cloud.currentid()
        for id in range(currentid-5,currentid+1):
            cloud.analysis(id,n)
            print 'eid',id,'done'
        print "finish,sleep 15 min"
        time.sleep(900)
