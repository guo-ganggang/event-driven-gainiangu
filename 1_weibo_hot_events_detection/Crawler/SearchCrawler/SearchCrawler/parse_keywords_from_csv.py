#coding=utf-8
from models import Keyword
from daos import Keyword as DB_Keyword
from datetime import datetime

if __name__ == '__main__':

    keyword_list = []

    file_path = '/Users/ZHU_Chenghao/Downloads/keywords.csv'
    with open(file_path, 'r') as reader:
        lines = reader.readlines()[1:]  # remove the header
        for line in lines:
            elements = line.split(',')
            timestamp = elements[0]
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            score = int(elements[-1].strip('\n'))
            keywords = elements[1:-1]
            for keyword in keywords:
                keyword = eval(keyword.strip('["]'))

            keyword_list.append(Keyword(cid=0, keyword=keyword, timestamp=timestamp, score=score))

    print 'Parse Done!'

    print 'Add keywords into database...'
    DB_Keyword.dump_keywords(keyword_list)
    print 'Dumping Done!'
