#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 4/7/2017 上午 10:47
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : data_process.py
# @Software: PyCharm

import json
import codecs
import os
from itertools import islice
import re
import urllib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def parser_json(file_json,filepath,fileName):

    words_kernel = [u'股',u'金融',u'股份',u'投资',u'资本',u'经济',u'私募',u'短线',u'理财',u'证券',u'顾问',u'财经',u'分析师',u'交易',u'研究',u'互联网']
    belong_common_key_word = False
    for k in range(len(words_kernel)):
        if words_kernel[k] in fileName:
            belong_common_key_word = True
            break
    try:
        data = json.loads(file_json)
        cards = data['cards']
        for card in cards:
            if card['card_type'] == 11:
                card_groups = card['card_group']
                select_k = 1
                if (len(card_groups) == 2) and (belong_common_key_word == True):
                    select_k = 2
                # if len(card_groups) > 3:
                #     select_k = 3

                elif (len(card_groups) > 2) and (belong_common_key_word == True):
                    select_k = 3
                # else:
                #     select_k = len(card_groups)

                with codecs.open(filepath + 'caijing_weibo_uid_info_third.csv', "a+", "utf-8") as outfile_total:
                    for j in range(select_k):
                        card_group = card_groups[j]
                        user = card_group['user']
                        id = user['id']
                        screen_name = user['screen_name']
                        level = user['level']

                        followers_count = user['followers_count']
                        if u'万' in unicode(followers_count):
                            followers_counts = filter(str.isdigit, str(followers_count)) + '0000'
                        else:
                            followers_counts = followers_count

                        friends_count = user['friends_count']
                        if u'万' in unicode(friends_count):
                            followees_counts = filter(str.isdigit, str(friends_count)) + '0000'
                        else:
                            followees_counts = friends_count
                        # userType_des = card_group['desc1'].encode("utf-8")
                        # p = re.compile('\s+')
                        # new_userType_des = re.sub(p, '', userType_des)
                        # followees_count_des = card_group['desc2'].encode("utf-8")
                        # followees_count = filter(str.isdigit, followees_count_des)
                        outfile_total.write(
                            str(id) + '\t' + str(screen_name) + '\t' + str(level) + '\t' + str(followers_counts) + \
                           '\t' + str(followees_counts)  + '\n')

    except KeyError as e:
        print "KeyError: 'cards' "
        print u"解析出错，放弃！ ", fileName
    except ValueError as e:
        print "ValueError: 'Extra data' "
        print u"解析出错，放弃！ ", fileName


def dedup(filepath):
    uid_info = {}
    inFilePath_1 = filepath + 'stock_weibo_info_3.csv'
    inFilePath_2 = filepath + 'caijing_weibo_uid_info_third_dedup.csv'
    outFilePath = filepath + 'caijing_weibo_uid_info_thi_fou_dedup.csv'
    with codecs.open(inFilePath_1, "rb", "utf-8") as dedup_input_file1:
        for line in islice(dedup_input_file1.readlines(), 1, None):
            temp_info = []
            temp1 = line.strip().split('	')
            if len(temp1) < 6:
                continue
            if temp1[1] not in uid_info.keys():
                temp_info.append(temp1[2])
                temp_info.append(temp1[5])
                temp_info.append(temp1[3])
                uid_info[temp1[1]] = temp_info
            else:
                continue

    with codecs.open(inFilePath_2, "rb", "utf-8") as dedup_input_file2:
        for line in islice(dedup_input_file2.readlines(), 1, None):
            temp_info = []
            temp2 = line.strip().split('	')
            if len(temp2) < 5:
                continue
            if temp2[0] not in uid_info.keys():
                temp_info.append(temp2[1])
                temp_info.append(temp2[3])
                temp_info.append(temp2[4])
                uid_info[temp2[0]] = temp_info
            else:
                continue

    with codecs.open(outFilePath, "w", "utf-8") as dedup_output_file:
        for key in uid_info.keys():
            temp = '	'.join(uid_info[key])
            dedup_output_file.write(key+'	'+ temp + '\n')

def dedup2(filepath):
    uid_info = set()
    inFilePath = filepath + 'caijing_weibo_uid_all.csv'
    outFilePath = filepath + 'caijing_weibo_uid_info_thi_fou_dedup.csv'
    with codecs.open(outFilePath, "w", "utf-8") as output_file:
        with codecs.open(inFilePath, "rb", "utf-8") as input_file:
            for line in islice(input_file.readlines(), 0, None):
                temp = line.strip()
                if temp in uid_info:
                    continue
                else:
                    output_file.write(line)
                    uid_info.add(temp)

def dedup3(filepath):
    uid_info = set()
    inFilePath_1 = filepath + 'caijing_weibo_uid_temp.csv'
    inFilePath_2 = filepath + 'caijing_weibo_uid_info_thi_fou_dedup_top_select.csv'
    outFilePath = filepath + 'caijing_weibo_uid_2-2.csv'
    with codecs.open(inFilePath_1, "rb", "utf-8") as dedup_input_file1:
        for line1 in islice(dedup_input_file1.readlines(), 0, None):
            temp1 = line1.strip()
            uid_info.add(temp1)

    with codecs.open(outFilePath, "w", "utf-8") as dedup_output_file:
        with codecs.open(inFilePath_2, "rb", "utf-8") as dedup_input_file2:
            for line2 in islice(dedup_input_file2.readlines(), 0, None):
                temp2 = line2.strip()
                if temp2 not in uid_info:
                    dedup_output_file.write(line2)


def weibo_account_influence_score(filepath):
    inFilePath = filepath + 'caijing_weibo_uid_info_thi_fou_dedup.csv'
    outFilePath = filepath + 'caijing_weibo_uid_info_thi_fou_dedup_top_select.csv' #_select
    uid_score = {}
    with codecs.open(inFilePath, "rb", "utf-8") as is_input_file:
        for line in islice(is_input_file.readlines(), 1, None):
            temp = line.strip().split('\t')
            if len(temp) == 4:
                # print temp[2],temp[3],temp[4]
                score = 0.3 * int(temp[2]) + 0.167 * int(temp[3])
                # print score
            else:
                continue
            uid_score[temp[0]] = score

    hist_sorted = sorted(uid_score.iteritems(), key=lambda d: d[1], reverse=True)

    with codecs.open(outFilePath, "a+", "utf-8") as output_file:
        for i in range(90000):  # len(hist_sorted)
            # print hist_sorted[i][0],hist_sorted[i][1]    + "," + str(hist_sorted[i][1])
            # output_file.write(hist_sorted[i][0]+'\t'+str(hist_sorted[i][1]) + '\n')
            output_file.write(hist_sorted[i][0] + '\n')


if __name__ == '__main__':
    filepath = 'D:\\SMU_WORK\\stock_weibo_account_info\\'
    # with codecs.open(filepath + 'caijing_weibo_uid_info_third.csv', "a+", "utf-8") as output_file:
    #     output_file.write('uid' + '\t' + 'screen_name' + '\t' + 'level' + '\t' + 'followers_count' + '\t' + \
    #                       'followees_count' + '\n')
    # fileNameFeature = '.csv'
    # upath = unicode(filepath + 'out_josn_files_7\\','utf-8')
    # fileNameLabels = [f for f in os.listdir(upath) if f.endswith(fileNameFeature)]
    #
    # print len(fileNameLabels)
    #
    # for fileName in fileNameLabels:
    #     # print filepath + 'out_josn_files_2\\' + fileName.decode("utf-8")
    #     fp = open(filepath + 'out_josn_files_7\\' + fileName.decode("utf-8"))
    #     first_line = fp.readline()
    #     req_text = first_line.strip()
    #     parser_json(req_text,filepath,fileName)
    #
    # dedup(filepath)
    weibo_account_influence_score(filepath)

    dedup3(filepath)


