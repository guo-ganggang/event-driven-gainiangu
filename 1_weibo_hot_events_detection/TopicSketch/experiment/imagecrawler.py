__author__ = 'bchang'

import requests
from lxml import etree
from timeout import timeout


class ImageCrawler:
    """ required libraries:  requests-2.7.0, lxml-3.4.4 """
    def __init__(self):
        self.map = dict()

    def extractForTwitter(self, htmlDom):
        """twitter.com"""
        imgURL = ""
        # twitter: single image
        nodes = htmlDom.xpath(u'//div[@class="cards-base cards-multimedia"]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        else:
            # twitter: multiple images
            nodes = htmlDom.xpath(u'//div[@class="cards-base cards-multimedia"]//div[@data-resolved-url-large]')
            if len(nodes) > 0:
                imgURL = nodes[1].attrib['data-url']
        return imgURL

    def extractForWattpad(self, htmlDom):
        """ www.wattpad.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="cover cover-lg"]/img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForChannelNewsAsia(self, htmlDom):
        """ www.channelnewsasia.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@id="photo-tab"]//div[@class="main-slide"]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForVine(self, htmlDom):
        """ vine.co """
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    def extractForImgur(self, htmlDom):
        """ i.imgur.com and imgur.com"""
        #(u'i.imgur.com', 6)
        #(u'imgur.com', 4)

        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="image textbox"]/img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForNea(self, htmlDom):
        """ www.nea.gov.sg """
        imgURL = "http://www.nea.gov.sg/Html/Nea/images/common/logo.jpg"
        return imgURL

    def extractForAllkpop(self, htmlDom):
        """ www.allkpop.com """
        imgURL = ""
        nodes = htmlDom.xpath(u'//div[@class="row-fluid category5"]//section[@class="post "]//img')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['src']
        return imgURL

    def extractForDaumcdn(self, htmlDom):
        """ t1.daumcdn.net """
        imgURL = ""
        return imgURL

    def extractForInstagram(self, htmlDom):
        """ instagram.com """
        #(u'i.instagram.com', 1)
        #(u'instagram.com', 3)
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    def extractForStaticflickr(self, htmlDom):
        """ staticflickr.com """
        #(u'farm1.staticflickr.com', 3)
        #(u'farm6.staticflickr.com', 1)
        imgURL = ""
        nodes = htmlDom.xpath(u'//meta[@property="og:image"]')
        if len(nodes) > 0:
            imgURL = nodes[0].attrib['content']
        return imgURL

    @timeout(15)
    def crawl(self, url):
        if url in self.map:
            return self.map[url]

        """ get the img-url from a web page. """
        imgURL = ""
        try:
            r = requests.get(url)
            #print url, r.url
            paths = r.url.split("/")

            if r.url.endswith((".jpg",'.png','.gif','.jpeg')):
                imgURL = r.url
            else:
                htmlDom = etree.HTML(r.content.decode('utf-8'))
            if imgURL == "":
                imgURL = self.extractForTwitter(htmlDom)
            if imgURL == "":
                imgURL = self.extractForWattpad(htmlDom)
            if imgURL == "":
                imgURL = self.extractForChannelNewsAsia(htmlDom)
            if imgURL == "":
                imgURL = self.extractForVine(htmlDom)
            if imgURL == "":
                imgURL = self.extractForImgur(htmlDom)
            if imgURL == "" and "nea.gov" in paths[2]:
                imgURL = self.extractForNea(htmlDom)
            if imgURL == "":
                imgURL = self.extractForAllkpop(htmlDom)
            if imgURL == "":
                imgURL = self.extractForDaumcdn(htmlDom)
            if imgURL == "":
                imgURL = self.extractForInstagram(htmlDom)
            if imgURL == "":
                imgURL = self.extractForStaticflickr(htmlDom)
            if imgURL != "" and "http://" not in imgURL and "https://" not in imgURL:
                imgURL = paths[0] + "/" + paths[1] + "/" + paths[2] + "/" + imgURL
        except Exception as e:
            print e

        if imgURL == 'https://abs.twimg.com/errors/logo23x19.png':
            print 'crawl image from Twitter: error.'  # debugging
            imgURL = None

        if imgURL == "":
            imgURL = None

        self.map[url] = imgURL
        return imgURL


if __name__ == '__main__':
    ic = ImageCrawler()
    urls = [
        'http://t.co/O310hcutb0',
        'http://t.co/DNgoMhzQyS',
        'http://t.co/O310hcutb0',
    ]

    for url in urls:
        print ic.crawl(url)
