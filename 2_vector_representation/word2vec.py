#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/19 12:32
# @Author  : GUO Ganggang
# @Site    : 
# @File    : word2vec.py
# @Software: PyCharm

import sys
import codecs
import gensim
import numpy

reload(sys)
sys.setdefaultencoding('utf-8')

def dedup_statistic(filePath):
    words_set = set()
    infilePath = filePath + 'gainiangu_Name_select.csv'
    outfilePath = filePath + 'gainiangu_extend_words_dict.csv'
    with codecs.open(infilePath, "rb", "utf-8") as inputStockCode:
        for line in inputStockCode:
            temp = line.strip().split(',')
            if len(temp) < 2:
                print line.strip()
                continue
            for word in temp[1:]:
                words_set.add(word)
    print len(words_set)

    with codecs.open(outfilePath, "w", "utf-8") as output_file:
        for word in words_set:
            output_file.write(word + '\n')


def similarly_words_by_w2v(filePath):
    word2vec_model_path = 'H:\\temp\\word2vec\\weibo_news_xueqiu_ugc_w2v_s128_w3_m50.vector'
    model = gensim.models.Word2Vec.load_word2vec_format(word2vec_model_path, binary=False)
    inFilePath = filePath + 'gainiangu_description_tfidf_10words.csv'
    outfilePath = filePath + 'gainiangu_description_tfidf_10words_embedding.csv'

    gainian_name_words = {}
    with codecs.open(inFilePath, "rb", "utf-8") as inputfile:
        for line in inputfile:
            temp = line.strip().split('\t')
            if len(temp) != 2:
                print line.strip()
                continue
            gainian_name_words[temp[0]] = temp[1]
    print len(gainian_name_words)

    with codecs.open(outfilePath, "w", "utf-8") as output_file:
        for key in gainian_name_words.keys():
            # word = utils.to_unicode(word)
            word_row = []
            # print word
            # words_set_dirc.add(word)
            words_list = gainian_name_words[key].strip().split(',')
            a = numpy.zeros(shape=(128,))
            for word in words_list:

                try:
                    # results = model.most_similar(word, topn=5)
                    word_row = model[word]
                    # print word_row.tolist()
                    a += word_row
                except KeyError:
                    # output_file.write(word + '\n')
                    continue
                # for e in results:
                    # print e[0], e[1]
                    # if e[1] > 0.45:
                        # word_row.append(','.join([str(var) for var in e[0:2]]))
                        # words_set_dirc.add(e[0])
            a = a / len(words_list)
            # similarly_words = ' '.join(word_row)
            vec = ','.join([str(value) for value in a.tolist()])
            output_file.write(key + '\t' + vec + '\n')

    # with codecs.open(outfilePath, "w", "utf-8") as output_file:
    #     for word in words_set_dirc:
    #         output_file.write(word + '\n')

def similarly_words_extend_by_w2v(filePath):
    word2vec_model_path = 'H:\\temp\\word2vec\\news_12g_baidubaike_20g_novel_90g_embedding_64.bin'

    inFilePath = filePath + 'gainiangu_description_tfidf_Nwords_makeup.csv'
    outfilePath = filePath + 'gainiangu_description_tfidf_Nwords_makeup_extend_by_w2v_2.csv'

    gainian_name_words = {}
    with codecs.open(inFilePath, "rb", "utf-8") as inputfile:
        for line in inputfile:
            temp = line.strip().split('\t')
            if len(temp) != 2:
                print line.strip()
                continue
            words_dedup = set()
            text_words = temp[1].strip().split(',')
            for i in range(len(text_words)):
                words_dedup.add(text_words[i])
            gainian_name_words[temp[0]] = words_dedup
    print len(gainian_name_words)

    model = gensim.models.Word2Vec.load_word2vec_format(word2vec_model_path, binary=True)
    gainian_name_words_extend = {}
    for key in gainian_name_words.keys():
        extend_words = set()
        extend_words.add(key)
        try:
            results = model.most_similar(key, topn=3)
            for e in results:
                # print e[0], e[1]
                extend_words.add(e[0])
        except KeyError:
            print 'KeyError',key

        if len(gainian_name_words[key]) > 20:
            for word in gainian_name_words[key]:
                extend_words.add(word)

        elif(10 < len(gainian_name_words[key]) <= 20):
            for word in gainian_name_words[key]:
                extend_words.add(word)
                try:
                    results = model.most_similar(word, topn=2)
                    for e in results:
                        # print e[0], e[1]
                        extend_words.add(e[0])
                except KeyError:
                    print 'KeyError', word

        elif (len(gainian_name_words[key]) <= 10):
            for word in gainian_name_words[key]:
                extend_words.add(word)
                try:
                    results = model.most_similar(word, topn=3)
                    for e in results:
                        # print e[0], e[1]
                        extend_words.add(e[0])
                except KeyError:
                    print 'KeyError', word
        gainian_name_words_extend[key] = extend_words
    print len(gainian_name_words_extend)

    with codecs.open(outfilePath, "w", "utf-8") as output_file:
        for key in gainian_name_words_extend.keys():
            words_list = list(gainian_name_words_extend[key])
            words_str  = ','.join(words_list)
            output_file.write(key + '\t' + words_str + '\n')



if __name__ == '__main__':
    filePath = 'H:\\temp\\\intelligence_concept_stock\\events_gainians_stocks_models_dataset\\'
    # dedup_statistic(filePath)
    # similarly_words_by_w2v(filePath)
    similarly_words_extend_by_w2v(filePath)