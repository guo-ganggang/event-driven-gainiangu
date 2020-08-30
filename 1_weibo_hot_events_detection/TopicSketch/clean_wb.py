# coding=utf-8

import re

from snownlp import SnowNLP

class Clean_Wb:

    def __init__(self):

        self.emotion_reg = re.compile(r"\[.+?\]")
        self.at_reg = re.compile(r"(@.+?[\\s: ])")
        self.atend_reg = re.compile(r"(@.+?$)")
        self.url_reg = re.compile(r"http://t.cn/\w{0,15}")
        self.topic_reg = re.compile(r"#")
        self.zf_reg = re.compile(ur"转发微[薄|博]")
        self.punc_reg = re.compile(ur"[★~!$^&*()=|{}':;'.<>/ˉ﹃ ≥≤﹏?~！￥……&*（）——|【】‘；：”“'。，、？]")

    def re_punc(self,weibo):
        return re.sub(self.punc_reg,"",weibo).strip()

    def re_emotion(self,weibo):
        return re.sub(self.emotion_reg,"",weibo)

    def re_at(self,weibo):
        weibo = re.sub(self.at_reg,"",weibo)
        return re.sub(self.atend_reg,"",weibo)

    def re_url(self,weibo):
        return re.sub(self.url_reg,"",weibo)

    def re_topic(self,weibo):
        return re.sub(self.topic_reg,"",weibo)

    def rm_rt(self,weibo):
        wblist = weibo.split(r"//")

        re_list = []

        for wl in wblist:
            wls = wl.strip()
            if wls != "":
                re_list.append(wls)

        return " ".join(re_list)

    def re_zf(self,weibo):
        return re.sub(self.zf_reg,"",weibo)

    def clean_wb(self,weibo):

        s = SnowNLP(weibo)
        weibo = s.han
        weibo = self.re_at(weibo)
        weibo = self.re_emotion(weibo)
        weibo = self.re_url(weibo)
        weibo = self.rm_rt(weibo)

        if self.re_punc(weibo) == "":
            return ""
        else:
            return weibo.strip()


if __name__ == "__main__":

    cw = Clean_Wb()
    print cw.clean_wb(u"【连续5天气温超22℃！昨起#合肥正式入夏#[微风]】@安徽昨日 [lol] 全省大部分地区最高温25℃～29℃之间，最高宿松和绩溪29.1℃。当天合肥平均气温24.9℃，已连续5天平均气温超22℃。从气象学意义上来说，合肥已经入夏啦！不过伴随夏天而来的，是未来一段时间的阴雨天哦！O网页链接 夏天标配↓↓")
