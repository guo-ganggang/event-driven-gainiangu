import urllib, urllib2
import ssl
import json
from configs import ACC_ACCESS_LIMIT


class Downloader(object):
    def __init__(self):
        self.base_api = 'https://api.weibo.cn/2/cardlist' \
                   '?networktype=wifi&extparam=filter_type%3Drealtimehot%26mi_cid%3D230926%26pos%3D0' \
                   '&uicode=10000003&moduleID=708&featurecode=10000085&lcardid=hot_search&c=android&i=b02c74a' \
                   '&ua=OPPO-OPPO%20R9%20Plusm%20A__weibo__6.10.0__android__android5.1.1' \
                   '&wm=9847_0002&aid=01AqnUvzp73TXy3GLdDRCQXansQh0WdGR_fMeitNbMEiHh-8k.&uid=6032206936&v_f=2' \
                   '&v_p=36&from=106A095010&imsi=460030765213241&lang=zh_CN&lfid=230926type%3D1%26t%3D3' \
                   '&skin=default&count=20&oldwm=9893_0044&sflag=1&luicode=10000003&container_ext=nettype%3Awifi' \
                   '&need_head_cards=1'
        self.api = ''
    def group_api(self, account, keyword, page):
        self.api = self.base_api

        s = '&s=' + account.s  # s maybe stands for different accounts
        gsid = '&gsid=' + account.gsid

        keyword = keyword.encode('utf8')
        keyword = urllib.quote(keyword)
        fid = '&fid=230926type%3D1%26q%3D' + keyword + '%26t%3D0'
        containerid = '&containerid=230926type%3D1%26q%3D' + keyword + '%26t%3D0'

        page = '&page=%d' % (page,)

        self.api = self.api + s + gsid + fid + containerid + page

    def download(self, account, keyword, page):
        self.group_api(account, keyword, page)

        context = ssl._create_unverified_context()
        while True:
            if account.count > ACC_ACCESS_LIMIT:
                return None  # account runs out of access times
            try:
                data = urllib2.urlopen(self.api, context=context).read()
                account.count += 1
                return json.loads(data)
            except Exception as e:
                account.count += 1
                print e