from crawler import Crawler

if __name__ == '__main__':
    my_crawler = Crawler()
    while True:
        my_crawler.search_and_get_related_timelines()
        my_crawler.update_keywords()