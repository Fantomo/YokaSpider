# -*- coding: utf-8 -*-
import scrapy
from YokaSpider.items import YokaspiderItem

import os, re


class YokaSpider(scrapy.Spider):
    name = 'yoka'
    allowed_domains = ['yoka.com']
    start_urls = ['http://beauty.yoka.com/']

    def parse(self, response):

        items = []

        # 美容下的所有子类
        sub_urls = response.xpath("//div[@class='twoNav']/div/a/@href").extract()
        sub_titles = response.xpath("//div[@class='twoNav']/div/a/text()").extract()

        for i in range(0, len(sub_urls)):

            if sub_urls[i].startswith('http://www.yoka.com/beauty/'):
                item = YokaspiderItem()
                # 子类目录
                sub_file_name = "./data/" + sub_titles[i]

                # 创建目录
                if not os.path.exists(sub_file_name):
                    os.makedirs(sub_file_name)

                item['sub_title'] = sub_titles[i]
                item['sub_url'] = sub_urls[i]
                item['sub_file_name'] = sub_file_name

                items.append(item)

        for item in items:
            yield scrapy.Request(url=item['sub_url'], meta={'data': item}, callback=self.second_parse)


    def second_parse(self, response):

        meta_data = response.meta['data']

        # # 文章 标题
        article_titles = response.xpath("//div[@class='tit']/a/text()").extract()
        # 文章 url
        article_urls = response.xpath("//div[@class='tit']/a/@href").extract()

        items = []

        # 爬文章url
        for i in range(0, len(article_urls)):
            if article_urls[i].startswith(meta_data['sub_url']) and article_urls[i].endswith(".shtml"):
                item = YokaspiderItem()
                # 文章目录
                article_file_name = meta_data['sub_file_name'] + "/" + article_titles[i]
                # 创建文章文件夹
                if not os.path.exists(article_file_name):
                    os.makedirs(article_file_name)

                # 保存文章 url, title, filename
                item['sub_title'] = meta_data['sub_title']
                item['sub_url'] = meta_data['sub_url']
                item['sub_file_name'] = meta_data['sub_file_name']
                item['article_url'] = article_urls[i]
                item['article_file_name'] = article_file_name

                items.append(item)

        for item in items:
            yield scrapy.Request(item['article_url'], meta={'data': item}, callback=self.article_parse)


    def article_parse(self, response):

        pattern = re.compile(r"/pic\d+.shtml$")

        if not pattern.search(response.url):

            item = response.meta['data']
            # 标题
            item['article_title'] = self.get_article_title(response)
            # 摘要
            item['article_quote'] = self.get_article_quote(response)
            # 内容
            item['article_content'] = self.get_article_content(response)
            # 标签
            item['article_tag'] = self.get_article_tag(response)
            # 图片
            item['article_imgs'] = self.get_article_imgs(response)
            # 图片名字
            item['img_names'] = self.get_img_names(response)

            next_page = self.get_next_page(response)
            print "next_page:", next_page
            if next_page:
                next_page_url = "http://www.yoka.com" + next_page
                print "next_page_url:", next_page_url
                yield scrapy.Request(url=next_page_url, meta={'data':item}, callback=self.article_parse)
        else:
            pass

        yield item


    def get_article_title(self, response):
        article_title = response.xpath("//div[@class='gLeft']/h1/text()").extract()
        if len(article_title):
            article_title = article_title[0]
        else:
            article_title = 'NULL'
        return article_title

    def get_article_content(self, response):
        article_content = response.xpath("//div[@class='textCon']/p/text()").extract()
        if len(article_content):
            article_content = "".join(article_content)
        else:
            article_content = 'NULL'
        return article_content

    def get_article_quote(self, response):
        article_quote = response.xpath("//div[@class='double_quotes']/div/text()").extract()
        if len(article_quote):
            article_quote = article_quote[0]
        else:
            article_quote = 'NULL'
        return article_quote

    def get_article_tag(self, response):
        article_tag = response.xpath("//div[@class='navTag']/a/text()").extract()
        if len(article_tag):
            article_tag = ",".join(article_tag)
        else:
            article_tag = 'NULL'
        return article_tag

    def  get_article_imgs(self, response):
        article_imgs = response.xpath("//div[@class='textCon']/div[@class='editer_pic']//img/@src").extract()
        if len(article_imgs):
            article_imgs = article_imgs
        else:
            article_imgs = 'NULL'
        return article_imgs

    def get_img_names(self, response):
        img_names = response.xpath("//div[@class='editer_pic']/i/text()").extract()
        if len(img_names):
            img_names = img_names
        else:
            img_names = 'NULL'
        return img_names

    def get_next_page(self, response):
        next_page = response.xpath("//div[@class='pages']/a[@class='next']/@href").extract()
        if next_page:
            next_page = next_page[0]
        else:
            next_page = False
        return next_page
