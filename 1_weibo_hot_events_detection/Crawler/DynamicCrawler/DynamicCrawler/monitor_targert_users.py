from Crawler import Crawler

if __name__ == '__main__':

    crawler = Crawler()

    print 'Start to monitor...'
    try:
        crawler.monitor()
    except Exception as e:
        print e
    finally:
        crawler.reset_buffer()
        print 'Stop monitoring!'


