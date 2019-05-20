# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YokaspiderItem(scrapy.Item):

    # 小类
    sub_title = scrapy.Field()
    sub_url = scrapy.Field()
    # 小类存储路径
    sub_file_name = scrapy.Field()
    # 文章链接
    article_url = scrapy.Field()
    # 文章文件夹
    article_file_name = scrapy.Field()
    # 文章标题
    article_title = scrapy.Field()
    # 文章内容
    article_content = scrapy.Field()
    # 文章图片
    article_imgs = scrapy.Field()
    # 图片
    img_url = scrapy.Field()
    # 图片描述
    img_names = scrapy.Field()
    # 文章引用
    article_quote = scrapy.Field()
    # 文章标签
    article_tag = scrapy.Field()
