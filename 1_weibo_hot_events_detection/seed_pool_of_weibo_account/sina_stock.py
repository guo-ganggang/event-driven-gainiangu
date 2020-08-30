#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import time
import codecs
from random import randint
from itertools import islice

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#raise ConnectionError(e, request=request)
#requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.weibo.cn', port=443): Max retries exceeded with url: /2/page?networktype=wifi&uicode=10000011&moduleID=708&featurecode=10000085&wb_version=3342&lcardid=seqid%3A569949735%7Ctype%3A32%7Ct%3A%7Cpos%3A1-0-1%7Cq%3A%E4%B8%AD%E5%9B%BD%E5%B9%B3%E5%AE%89%7Cext%3A%26type%3Dstock%26object_id%3D1022%3A230677sh601318%26&c=android&i=b02c74a&s=f0b359ea&ua=OPPO-OPPO%20R9%20Plusm%20A__weibo__7.3.0__android__android5.1.1&wm=9847_0002&aid=01AqnUvzp73TXy3GLdDRCQXansQh0WdGR_fMeitNbMEiHh-8k.&fid=230677sh601318&v_f=2&v_p=45&from=1073095010&gsid=_2A2512k0KDeRxGeBO6FMX9inEyjuIHXVUJs11rDV6PUJbkdANLVDykWpmNqcxEmVCJyQrdonMHKNlzXVs9A..&imsi=460030765213241&lang=zh_CN&lfid=100303type%3D32%26q%3D%E4%B8%AD%E5%9B%BD%E5%B9%B3%E5%AE%89&skin=default&count=20&oldwm=9893_0044&sflag=1&luicode=10000003&containerid=230677sz000558&page_id=230677shsz000558&page=10 (Caused by NewConnectionError('<requests.packages.urllib3.connection.VerifiedHTTPSConnection object at 0x0000000005B94BA8>: Failed to establish a new connection: [Errno 11004] getaddrinfo failed',))


def generate_url(i_stock_code, i_page_num):
    s_containerid = '&containerid=230677%s' % (i_stock_code,)
    s_page_id = '&page_id=230677sh%s' % (i_stock_code,)
    s_page = '&page=%d' % (i_page_num,)
    return s_BASE_URL + s_containerid + s_page_id + s_page


# stock = 'sh000001'
def obtain_stock_codes(file_path):
	stocks = []
	with codecs.open(file_path + 'hs_stock_code_0403.csv', "rb", "utf-8") as inputfile:
		for line in islice(inputfile.readlines(), 0, None):
			stocks.append(line.strip())
	return stocks

def crawl_data(stocks,file_path):
	for i in range(len(stocks)):
		page = 2
		stock = stocks[i]
		finished_obtain_pages = 0
		error_obtain_pages = 0
		while(True):
			if page>100:
				break
			response = requests.get(generate_url(stock, page), headers=d_HEADERS)
			print(response.status_code)
			if response.status_code != 200:
				break

			data = json.loads(response.text)  # unicode

			hasWeibo = False

			try:
				cards = data['cards']
			except KeyError as e:
				print "KeyError: 'cards'"
				error_obtain_pages += 1
				page += 1
				continue

			with codecs.open(file_path + 'stock_weibo_parsed_%s.csv'%stock, 'a', 'utf-8') as outfile:
				for card in cards:
					if card['card_type'] == 11:
						hasWeibo = True
						card_groups = card['card_group']
						for card_group in card_groups:
							mblog = card_group['mblog']
							mid = mblog['mid']
							outfile.write(str(stock) + '\t' + str(page) + '\t' + str(mid) + '\t' + json.dumps(mblog) + '\n')

			if not hasWeibo:
				error_sleep = 10
				print('error crawling page %d, sleep %d seconds'% (page,error_sleep))
				error_obtain_pages += 1
				time.sleep(10)
				page += 1
				continue

			with codecs.open(file_path + 'stock_weibo_%s.csv' % stock, 'a', 'utf-8') as outfile:
				outfile.write(str(stock) + '\t' + str(page) + '\t' + json.dumps(data) + '\n')

			rand = randint(5,10)
			finished_obtain_pages += 1
			print('finished crawling page %d, sleep %d seconds'% (page,rand))
			page += 1
			time.sleep(rand)
		finished_every_stock = time.strftime('%Y-%m-%d', time.localtime(time.time()))
		print stock,str(finished_every_stock),str(finished_obtain_pages),str(error_obtain_pages)

if __name__ == '__main__':
	d_HEADERS = {
		'User-Agent': 'OPPO R9 Plusm A_5.1.1_weibo_7.3.0_android',
		'Accept-Encoding': 'gzip,deflate',
		'X-Log-Uid': '6031667817',
		'Host': 'api.weibo.cn',
		'Connection': 'Keep-Alive'
	}

	s_BASE_URL = 'https://api.weibo.cn/2/page?networktype=wifi&uicode=10000011&moduleID=708&featurecode=10000085' \
				 '&wb_version=3342&lcardid=seqid%3A569949735%7Ctype%3A32%7Ct%3A%7Cpos%3A1-0-1%7Cq%3A%E4%B8%AD%E5' \
				 '%9B%BD%E5%B9%B3%E5%AE%89%7Cext%3A%26type%3Dstock%26object_id%3D1022%3A230677sh601318%26&c=android' \
				 '&i=b02c74a&s=f0b359ea&ua=OPPO-OPPO%20R9%20Plusm%20A__weibo__7.3.0__android__android5.1.1&wm=9847_0002' \
				 '&aid=01AqnUvzp73TXy3GLdDRCQXansQh0WdGR_fMeitNbMEiHh-8k.&fid=230677sh601318&v_f=2&v_p=45&from=1073095010' \
				 '&gsid=_2A2512k0KDeRxGeBO6FMX9inEyjuIHXVUJs11rDV6PUJbkdANLVDykWpmNqcxEmVCJyQrdonMHKNlzXVs9A..&imsi=460030765213241' \
				 '&lang=zh_CN&lfid=100303type%3D32%26q%3D%E4%B8%AD%E5%9B%BD%E5%B9%B3%E5%AE%89&skin=default&count=20' \
				 '&oldwm=9893_0044&sflag=1&luicode=10000003'

	file_path = 'D:\\pingan_stock\\stockWeibo\\'
	stocks = obtain_stock_codes(file_path)
	crawl_data(stocks, file_path)