# -*- coding: utf-8 -*-
import json
import random
import scrapy
from scrapy import Request
from news.items import NewsItem
from fake_useragent import UserAgent
import time


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn']
    start_urls = []

    ua = UserAgent(verify_ssl=False)
    headers = {
        'User-Agent': ua.random,
    }
    # 全部、国内、国际、社会、体育、娱乐、军事、科技、财经、股市、美股
    category = {
        '1':"国内",'2':"国际",'3':'社会','4':'体育',
        '5':'娱乐','6':'军事','7':'科技','8':'财经','9':'股市','10':'美股'
    }
    lids = ['2509', '2510', '2511', '2669', '2512', '2513', '2514', '2515', '2516', '2517', '2518']
    index = 1
    page = 0
    count=0

    url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&num=50&page=%d&r=%f' % (lids[index], page, random.random())
    start_urls.append(url)

    def start_request(self):
        yield Request(self.start_urls, headers=self.headers)

    def parse(self, response):
        print("开始爬虫。。。")

        res = response.body_as_unicode()
        if res == '':
            print("response is null(403)")
        else:
            sites = json.loads(res)
            for i in range(10):
                for i in range(200):
                    for news in sites['result']['data']:
                        self.count += 1
                        request = scrapy.Request(news['url'], headers=self.headers, callback=self.parse_detail)
                        item = NewsItem()
                        item['title'] = news['title']
                        item['create_time'] = news['ctime']
                        item['url'] = news['url']
                        item['wap_url'] = news['wapurl']
                        item['summary'] = news['summary'].strip()
                        item['wap_summary'] = news['wapsummary']
                        item['intro'] = news['intro']
                        item['keywords'] = news['keywords']
                        item['content'] = ''.join(response.xpath('//*[@id="artibody"]/p/text()').extract()).replace(
                            u'\u3000\u3000', u'\n').replace(u'\xa0\xa0', u'\n').replace(u'\r\n', u'\n').replace(u'\n\r',
                                                                                                                u'\n').strip()
                        item['source'] = '新浪'
                        item['category'] = self.category.get(str(self.index))
                        yield item
                        if self.count == 49:
                            self.page += 1
                            self.url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&num=50&page=%d&r=%f' % (
                                self.lids[self.index], self.page, random.random())
                            print("翻页:" + self.url)
                            time.sleep(2)
                            yield scrapy.Request(self.url, headers=self.headers, callback=self.parse, dont_filter=True)
                self.index+=1



            # if len(sites['result']['data'])>0:
            #     for news in sites['result']['data']:
            #         # request = scrapy.Request(news['url'], headers=self.headers, callback=self.parse_detail)
            #         # request.meta['news'] = news
            #         # yield request
            #         print("页数："+str(self.page))
            #     print("结束1")
            #     self.page += 1
            #     self.url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&num=50&page=%d&r=%f' % (self.lids[self.index], self.page, random.random())
            #     print("翻页:" + self.url)
            #     time.sleep(2)
            #     yield scrapy.Request(self.url, headers=self.headers, callback=self.parse,dont_filter=True)
            # else:
            #     print("data null,url with new lid:")
            #     self.index += 1
            #     if self.index > len(self.lids):
            #         print("finish")
            #         return
            #     self.page = 0
            #     self.url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&num=50&page=%d&r=%f' % (self.lids[self.index], self.page, random.random())
            #     print(self.url)
            #     yield scrapy.Request(self.url, headers=self.headers, callback=self.parse)
            #     print("结束2")

        # self.page += 1
        # self.url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&num=50&page=%d&r=%f' % (self.lids[self.index], self.page, random.random())
        # print("翻页:"+self.url)
        # yield scrapy.Request(self.url, headers=self.headers, callback=self.parse)
        # print("结束3")


    def parse_detail(self, response):
        print("爬取信息。。。")
        item = NewsItem()
        news = response.meta['news']

        item['title'] = news['title']
        item['create_time'] = news['ctime']
        item['url'] = news['url']
        item['wap_url'] = news['wapurl']
        item['summary'] = news['summary'].strip()
        item['wap_summary'] = news['wapsummary']
        item['intro'] = news['intro']
        item['keywords'] = news['keywords']
        item['content'] = ''.join(response.xpath('//*[@id="artibody"]/p/text()').extract()).replace(u'\u3000\u3000', u'\n').replace(u'\xa0\xa0', u'\n').replace(u'\r\n', u'\n').replace(u'\n\r', u'\n').strip()
        item['source'] = '新浪'
        item['category'] = self.category.get(str(self.index))
        print("类别："+item['category'])

        yield item
        pass
