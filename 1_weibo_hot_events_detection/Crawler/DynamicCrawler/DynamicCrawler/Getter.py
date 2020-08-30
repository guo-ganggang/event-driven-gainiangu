import urllib2
import json
from Configuration import TIME_OUT, ACCESS_LIMIT


class Getter(object):
    def __init__(self):
        self.access_time = 0  # for public use
        self.access_counter = 0

        self.TIMELINE_API = 'http://api.weibo.cn/2/cardlist' \
                       '?uicode=10000198&featurecode=10000085&c=android' \
                       '&i=%s' \
                       '&s=%s' \
                       '&ua=smartisan-YQ601__weibo__5.6.0__android__android4.4.4' \
                       '&wm=14010_0013&aid=01Aibr-o0NOz4DajQJjFCwzZBT9aTJlCNWmr7y8ElZWcSPX6w.' \
                       '&fid=107603%s_-_WEIBO_SECOND_PROFILE_WEIBO&uid=3235744542' \
                       '&v_f=2&v_p=25&from=1056095010' \
                       '&gsid=%s' \
                       '&imsi=460070510304524&lang=zh_CN' \
                       '&page=%s' \
                       '&skin=default&count=20&oldwm=14010_0013' \
                       '&containerid=107603%s_-_WEIBO_SECOND_PROFILE_WEIBO' \
                       '&luicode=10000002&need_head_cards=0&sflag=1'
        # (i, s, fid, gsid, page, containerid)
        # different i, s and gsid decide different Weibo accounts
        # while fid and containerid are the target user's ID
        # page denotes page number



    def get_content(self, request_model, parameters):
        """

        :param request_model: a string, that's the API, which specifies which type of content you wanna get
        :param parameters: a tuple, corresponding parameters
        :return:
        """
        request_str = request_model % parameters
        request = urllib2.Request(request_str)

        while True:
            try:
                self.access_counter += 1
                response = urllib2.urlopen(request, timeout=TIME_OUT)
                return response.info(), json.loads(response.read())
            except Exception as e:
                print e
                try:
                    code = e.code
                    if code == 403:
                        return 403, 403
                except Exception as ex:
                    pass

                if self.access_counter > ACCESS_LIMIT:
                    return None, None

    def get_timeline(self, timeline_parameters):
        """

        :param timeline_parameters: a tuple
        :return:
        """

        message, body = self.get_content(self.TIMELINE_API, timeline_parameters)

        self.access_time = self.access_counter
        self.access_counter = 0

        if message == None and body == None:
            return None
        if message == 403:
            return 403

        return json.dumps(body, ensure_ascii=False).encode('utf-8')

    def get_user_timeline(self, uid, account_parameters, page=1):
        """

        :param uid: target user
        :param account_parameters:  combination of i, s and gsid
        :return:
        """
        i = account_parameters.i
        s = account_parameters.s
        gsid = account_parameters.gsid
        page = str(page)

        timeline_parameters = (i, s, uid, gsid, page, uid)

        return self.get_timeline(timeline_parameters)