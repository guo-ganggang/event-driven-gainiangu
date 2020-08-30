#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import imp
import codecs
import sys
import time
import json
from itertools import islice
from os import listdir

reload(sys)
sys.setdefaultencoding('utf-8')
import re

#according to the uid obtain the time
cursorObj = imp.load_source("dbCursor", "WeiboDBConnection.py")

def getBehavierData(output_path):
    with open(output_path, 'w') as output_file:
        sql = "select `commentid`,`content`,`attitude`,`repost`,`comments`,`ms` from stockweibo.pingan_stockcomment"
        try:
            con, cursor = cursorObj.getDBConnection()
            print sql
            cursor.execute(sql)
            person_rows = cursor.fetchall()
            num_weibo = len(person_rows)
            print num_weibo
            for person_row in person_rows:
                unix_date = person_row[5] / 1000
                timeArray = time.localtime(unix_date)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                # string = time.strptime(unix_date, '%Y-%m-%d %H:%M:%S')
                output_file.write(person_row[0] +  '\t' + person_row[1] +  '\t' + str(person_row[2]) \
                                  + '\t' + str(person_row[3]) + '\t' + str(person_row[4]) + '\t' + otherStyleTime + '\n')
            cursor.close()
            con.close()
        except MySQLdb.Error as e:
            print e


def getTianYanChaData(inputpath,outputpath):
    stock_code_company_name = {}
    with codecs.open(inputpath, "rb", "utf-8") as input_file:
        for line in islice(input_file.readlines(), 1, None):
            temp = line.strip().split('	')
            stock_code_company_name[temp[3]] = temp[0]

    print len(stock_code_company_name)

    with open(outputpath, 'w') as output_file:
        output_file.write(
            'stock_code' + '\t' + 'company_name' + '\t' + 'row[1]' + '\t' + 'row[2]' \
            + '\t' + 'row[3]' + '\n')
        try:
            con, cursor = cursorObj.getDBConnection()
            for key in stock_code_company_name.keys():
                sql = "select `name`,`legalRept`,`executiveInfo`,`shareholderInfo` from tianyancha.company where name = '%s'" % key
                print sql
                cursor.execute(sql)
                rows = cursor.fetchall()
                if len(rows) != 0:
                    for row in rows:
                        output_file.write(str(stock_code_company_name[key]) + '\t' +  str(row[0]) +  '\t' + str(row[1]) +  '\t' + str(row[2]) \
                                          + '\t' + str(row[3]) + '\n')
                else:
                    print 'empty!'
                    continue
            cursor.close()
            con.close()
        except MySQLdb.Error as e:
            print e

def getFinancialNewsData(output_path):
    with open(output_path, 'w') as output_file:
        sql = "SELECT title FROM finance_bbs.eastmoney_guba_post_pingan where bar_name = '光大银行吧' or bar_name = '光大证券吧'"
        # sql = "SELECT title FROM finance_bbs.eastmoney_guba_post_pingan where bar_name = '中国平安吧'"

        try:
            con, cursor = cursorObj.getDBConnection()
            print sql
            cursor.execute(sql)
            rows = cursor.fetchall()
            num_rows = len(rows)
            print num_rows
            for row in rows:
                output_file.write(str(row[0]) + '\n' )
            cursor.close()
            con.close()
        except MySQLdb.Error as e:
            print e


def obtainDataFromJson(file_path,outFile):
    fileNameFeature = 'stock_weibo_'
    fileNames = [f for f in listdir(file_path) if f.startswith(fileNameFeature)]
    with open(outFile, 'w') as output_file:
        for fileName in fileNames:
            print fileName
            stock_code = fileName[12:-4]
            inputpath = file_path + fileName
            with codecs.open(inputpath, "rb", "utf-8") as input_file:
                for line in islice(input_file.readlines(), 0, None):
                    temp = line.strip().split('\t')
                    data = json.loads(temp[2])  # unicode
                    try:
                        cards = data['cards']
                    except KeyError as e:
                        print "KeyError: 'cards'"
                        continue
                    for card in cards:
                        if card['card_type'] == 11:
                            card_groups = card['card_group']
                            for card_group in card_groups:

                                mblog = card_group['mblog']
                                # mid = mblog['mid']

                                text = mblog['text']
                                temp_text_list = text.strip().split('\n')
                                temp_text_str = ''.join(temp_text_list)
                                text_clean = temp_text_str.strip()

                                created_at = mblog['created_at']
                                date_str = re.sub(r'\+0800 ', '', created_at)
                                timeStamp = time.mktime(time.strptime(date_str, "%a %b %d %H:%M:%S %Y"))
                                timeArray = time.localtime(timeStamp)
                                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

                                reposts_count = mblog['reposts_count']
                                attitudes_count = mblog['attitudes_count']
                                comments_count = mblog['comments_count']

                                # user = mblog['user']
                                # uid = user['id']
                                # screen_name = user['screen_name']
                                # friends_count = user['friends_count']
                                # statuses_count = user['statuses_count']
                                # followers_count = user['followers_count']

                                output_file.write(stock_code + '\t' +  str(reposts_count) + '\t' +  \
                                                  str(attitudes_count) + '\t' +  str(comments_count) + '\t' + \
                                                  str(otherStyleTime) + '\t' + text_clean + '\n')
                                # output_file.write(str(otherStyleTime) + '\t' + text_clean + '\n')


def obtainData(output_path):
    with open(output_path, 'w') as output_file:
        sql = "SELECT uid,created_at,repost_num,favourite_num,comment_num,text FROM clear.timelines_history \
              WHERE created_at >= '2016-01-12 00:00:00' AND created_at <= '2016-04-15 22:00:00' \
              AND ( text like '%李玟%' OR text like '%李克勤%' OR text like '%信%' OR text like '%哈雅乐团%' OR text like '%徐佳莹%' OR  \
              text like '%关喆%' OR text like '%黄致列%' OR text like '%赵传%' OR text like '%苏运莹%' OR text like '%张信哲%' OR \
              text like '%王晰%' OR text like '%容祖儿%' OR text like '%金志文%' OR text like '%老狼%') \
              AND text like '%我是歌手%'"

        try:
            con, cursor = cursorObj.getDBConnection()
            print sql
            cursor.execute(sql)
            rows = cursor.fetchall()
            num_rows = len(rows)
            print num_rows
            for row in rows:
                output_file.write(str(row[0]) + '\t'  + str(row[1]) + '\t' + str(row[2]) + '\t'  + str(row[3]) + '\t' + str(row[4]) + '\t' + str(row[5]) +'\n')
            cursor.close()
            con.close()
        except MySQLdb.Error as e:
            print e

def obtainDataprofile(inputpath,output_path):
    distinct_uid = set()
    with codecs.open(inputpath, "rb", "utf-8") as input_file:
        for line in islice(input_file.readlines(), 0, None):
            temp = line.strip()
            distinct_uid.add(temp)
    print len(distinct_uid)

    with open(output_path, 'w') as output_file:
        for uid in distinct_uid:
            sql = "select `app_source`,`created_at`,`repost_num`,`favourite_num`,`comment_num` from FinancialWeibo.timelines_ggg where uid = '%s'" % uid
            try:
                con, cursor = cursorObj.getDBConnection()
                print sql
                cursor.execute(sql)
                rows = cursor.fetchall()
                num_rows = len(rows)
                print uid,str(num_rows)
                if num_rows == 0:
                    continue
                for row in rows:
                    output_file.write(str(uid) + '\t' + str(row[0]) + '\t'  + str(row[1]) + '\t' + str(row[2]) + '\t'  + str(row[3]) + '\t' + str(row[4]) +'\n')
                cursor.close()
                con.close()
            except MySQLdb.Error as e:
                print e


if __name__ == "__main__":
    # outPath = "D:\\pingan_stock\\pingan_stock.csv"
    # getBehavierData(outPath)
    # input = "D:\\pingan_stock\\tianyancha\\shangshi_company.csv"
    # outPath = "D:\\pingan_stock\\tianyancha\\shangshi_company_tianyancha.csv"
    # getTianYanChaData(input, outPath)


    # outPath = "D:\\pingan_stock\\pingan_stock_undervalueed\\guangda\\guangda_bbs.csv"
    # getFinancialNewsData(outPath)

    # file_path = 'D:\\pingan_stock\\weibo_word2vec\\'
    # outFile = 'D:\\pingan_stock\\weibo_word2vec\\stock_weibo.csv'


    # file_path = 'D:\\pingan_stock\\stockWeibo_dump\\'
    # inFile = file_path + 'stock_weibo_hkSSECOMP.csv'
    # outFile = 'D:\\pingan_stock\\stock_weibo.csv'
    # obtainDataFromJson(file_path,outFile)

    # outPath = "D:\\bisai\\IAMASINGER_Q4.csv"
    # obtainData(outPath)


    file_path = 'D:\\SMU_WORK\\stock_weibo_account_info\\scan_weibo_users\\'
    inFile = file_path + 'caijing_weibo_uid.csv'
    outFile = file_path + 'caijing_weibo_uid_post_info.csv'
    obtainDataprofile(inFile,outFile)

