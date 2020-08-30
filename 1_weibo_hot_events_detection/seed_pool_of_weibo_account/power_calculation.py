#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/27 14:13
# @Author  : GUO Ganggang
# @Site    : 
# @File    : power_calculation.py
# @Software: PyCharm

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
import datetime
import time
from itertools import islice
import pandas as pd

def MaxMinNormalization(x,Max,Min):
    x_Normalization = (x - Min) / (Max - Min)
    return x_Normalization
def Max_value(values):
    max = 0
    for i in range(len(values)):
        if max < values[i]:
            max = values[i]
    return max
def Min_value(values):
    min = 0
    for i in range(len(values)):
        if min > values[i]:
            min = values[i]
    return min

def compute_score(scores_list):
    weight_denominator = 0.0
    weight_molecular = len(scores_list)
    score = 0.0

    for j in range(len(scores_list)):
        weight_denominator += j
    for i in range(len(scores_list)):
        score = score + (weight_molecular / weight_denominator) * scores_list[i]
        weight_molecular = weight_molecular - 1
    return score

def days_from_age(datetime_list):
    days_com = []
    for i in range(len(datetime_list)):
        d1 = datetime.datetime.strptime(datetime_list[i], "%Y-%m-%d %H:%M:%S") #"%Y/%m/%d %H:%M:%S"
        d2 = datetime.datetime(2017,8,3)
        days = (d2 - d1).days
        days_com.append(float(days))
    return days_com

def profile_power_calcu(inFilePath,outFilePath):
    uid_score = {}
    uid_socres = {}
    title = []
    df = pd.read_csv(inFilePath,header=0)
    follower_num_max = Max_value(df['follower_num'].values)
    follower_num_min = Min_value(df['follower_num'].values)
    followee_num_max = Max_value(df['followee_num'].values)
    followee_num_min = Min_value(df['followee_num'].values)
    # print follower_num_max, followee_num_min
    weibo_num_max = Max_value(df['weibo_num'].values)
    weibo_num_min = Min_value(df['weibo_num'].values)
    level_max = Max_value(df['level'].values)
    level_min = Min_value(df['level'].values)
    # print level_max, level_min
    credit_score_max = Max_value(df['credit_score'].values)
    credit_score_min = Min_value(df['credit_score'].values)
    vip_level_max = Max_value(df['vip_level'].values)
    vip_level_min = Min_value(df['vip_level'].values)
    df['created_days'] = days_from_age(df['created_at'])
    # print df['created_days']
    created_days_max = Max_value(df['created_days'].values)
    created_days_min = Min_value(df['created_days'].values)
    # print created_days_max,created_days_min
    df['avg_day_weibo'] =df['weibo_num'].values / df['created_days'].values
    avg_day_weibo_max = Max_value(df['avg_day_weibo'].values)
    avg_day_weibo_min = Min_value(df['avg_day_weibo'].values)

    with codecs.open(inFilePath, "rb", "utf-8") as input:
        for line in islice(input.readlines(), 1, None):
            factors_list = []
            temp = line.strip().split(',')
            if len(temp) < 9:
                continue
            created_at = temp[1]
            d1 = datetime.datetime.strptime(created_at, "%Y/%m/%d %H:%M:%S")
            d2 = datetime.datetime(2017, 8, 3)
            days = (d2 - d1).days

            day_weibo = float(temp[4]) / float(days)
            created_days_score = MaxMinNormalization(float(days), created_days_max, created_days_min)
            follower_num_score = MaxMinNormalization(float(temp[2]), follower_num_max, follower_num_min)
            followee_num_score = MaxMinNormalization(float(temp[3]), followee_num_max, followee_num_min)
            weibo_num_score = MaxMinNormalization(float(temp[4]), weibo_num_max, weibo_num_min)
            level_score = MaxMinNormalization(float(temp[5]), level_max, level_min)
            credit_score_score = MaxMinNormalization(float(temp[6]), credit_score_max, credit_score_min)
            vip_level_score = MaxMinNormalization(float(temp[7]), vip_level_max, vip_level_min)
            day_weibo_score = MaxMinNormalization(day_weibo, avg_day_weibo_max, avg_day_weibo_min)

            # print created_days,follower_num,followee_num,weibo_num,level,credit_score,vip_level,day_weibo
            factors_list.append(day_weibo_score)
            factors_list.append(level_score)
            factors_list.append(weibo_num_score)
            factors_list.append(created_days_score)
            factors_list.append(vip_level_score)
            factors_list.append(followee_num_score)
            factors_list.append(follower_num_score)
            factors_list.append(credit_score_score)
            factors_list.append(float(temp[-1]))

            score = compute_score(factors_list)
            factors_list.append(score)
            uid_score[temp[0]] = score
            uid_socres[temp[0]] = factors_list

    hist_sorted = sorted(uid_score.iteritems(), key=lambda d: d[1], reverse=True)
    title.append('day_weibo')
    title.append('level')
    title.append('weibo_num')
    title.append('created_days')
    title.append('vip_level')
    title.append('followee_num')
    title.append('follower_num')
    title.append('credit_score')
    title.append('verified')
    title.append('total_score')
    with codecs.open(outFilePath, "w", "utf-8") as output_file:
        title_str = ','.join(title)
        output_file.write('uid' + ',' + title_str + '\n')
        for i in range(len(hist_sorted)):
            # print hist_sorted[i][0],hist_sorted[i][1]    + "," + str(hist_sorted[i][1])
            scores_str = ','.join(str(uid_socres[hist_sorted[i][0]][k]) for k in range(len(uid_socres[hist_sorted[i][0]])))
            output_file.write(hist_sorted[i][0]+','+scores_str + '\n')

def post_weibo_calcu(inFilePath,outFilePath):

    df = pd.read_csv(inFilePath, header=0)
    repost_num_max = Max_value(df['repost_num'].values)
    repost_num_min = Min_value(df['repost_num'].values)
    favourite_num_max = Max_value(df['favourite_num'].values)
    favourite_num_min = Min_value(df['favourite_num'].values)
    # print follower_num_max, followee_num_min
    comment_num_max = Max_value(df['comment_num'].values)
    comment_num_min = Min_value(df['comment_num'].values)
    df['created_days'] = days_from_age(df['created_at'])
    # print df['created_days']
    created_days_max = Max_value(df['created_days'].values)
    created_days_min = Min_value(df['created_days'].values)

    uid_num = {}
    with codecs.open(inFilePath, "rb", "utf-8") as input:
        for line in islice(input.readlines(), 1, None):
            temp = line.strip().split(',')
            uid_num[temp[0]] = uid_num.get(temp[0], 0) + 1

    uid_weibo_socre = {}
    with codecs.open(inFilePath, "rb", "utf-8") as input:
        for line in islice(input.readlines(), 1, None):

            temp = line.strip().split(',')
            created_at  = temp[2]
            d1 = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            d2 = datetime.datetime(2017, 8, 3)
            weibo_days = (d2 - d1).days

            repost_num = MaxMinNormalization(float(temp[3]), repost_num_max, repost_num_min)
            favourite_num = MaxMinNormalization(float(temp[4]), favourite_num_max, favourite_num_min)
            comment_num = MaxMinNormalization(float(temp[5]), comment_num_max, comment_num_min)
            created_days = MaxMinNormalization(float(weibo_days), created_days_max, created_days_min)
            score = (4 / 10.0 ) * repost_num + (3 / 10.0 ) * favourite_num + (2 / 10.0 ) * comment_num + (1 / 10.0 ) * (1-created_days)
            uid_weibo_socre[temp[0]] = uid_weibo_socre.get(temp[0], 0.0) + (1.0 / uid_num[temp[0]]) *score

    with codecs.open(outFilePath, "w", "utf-8") as output_file:
        for key in uid_weibo_socre.keys():
            output_file.write(key + ',' + str(uid_weibo_socre[key]) + '\n')


if __name__ == "__main__":
    file_path = 'D:\\SMU_WORK\\stock_weibo_account_info\\scan_weibo_users\\'
    inFile = file_path + 'caijing_weibo_uid_post_info.csv'
    outFile = file_path + 'users_financial_post_weibo_score.csv'
    # profile_power_calcu(inFile, outFile)
    post_weibo_calcu(inFile,outFile)



