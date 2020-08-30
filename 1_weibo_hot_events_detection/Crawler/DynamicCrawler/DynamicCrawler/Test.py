from Database import AccountParameters
from Parser import parse_timelines
import json
from Crawler import Crawler
from Object import TestMerge as TM
from Database import TestMerge

if __name__ == '__main__':

    # uid = '2574126482'
    # account_parameters = AccountParameters.get_account_parameters()
    # timeline = get_user_timeline(uid, account_parameters[0])
    #
    # with open('data.txt', 'w') as writer:
    #     writer.write(timeline)
    #
    # print 'Done!'

    # with open('data.txt', 'r') as reader:
    #     parse_timelines(reader.read())

    # crawler = Crawler()
    # crawler.monitor()

    i1 = TM(1, 3)
    i2 = TM(2, 5)

    item_list = []
    item_list.append(i1)
    item_list.append(i2)

    TestMerge.insert_items(item_list)