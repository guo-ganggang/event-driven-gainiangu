from Crawler import Crawler

if __name__ == '__main__':

    crawler = Crawler()

    print 'Start to reinforce.'
    try:
        crawler.reinforce()
    except Exception as e:
        print e
    finally:
        crawler.reset_buffer()
        print 'Crawler stops reinforcing.'
