# -*- coding: utf-8 -*-


import scrapy

from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline

import os, hashlib


class YokaspiderPipeline(object):

    def process_item(self, item, spider):

        # 文件夹名
        folder_name = item['article_file_name']
        # 文件名
        file_name = folder_name + "/" + item['article_title'] + '.txt'

        # 文章内容
        content = item['article_content']
        # 标签
        tag_name = item['article_tag']
        # 文章引用
        article_quote = item['article_quote']

        # 文章, 标签 写到本地
        with open(file_name, 'a')  as file:
            try:
                file.write("引用:" + article_quote.encode('utf-8') + '\n')
                file.write(content.encode('utf-8') + '\n')
                file.write("标签: " + tag_name.encode('utf-8') + '\n')
            except:
                print file_name,": encode error"

        # 图片信息
        img_info = folder_name + "/" + "img_info.txt"

        # 图片名字, url, sha1值写入本地
        for name, url in zip(item['img_names'], item['article_imgs']):
            sha1_name = hashlib.sha1(url).hexdigest()
            info = name.strip() + " => " + sha1_name + " => " + url
            with open(img_info, 'a') as f:
                f.write(info.encode('utf-8') + '\n')

        return item


class ImgPipeline(ImagesPipeline):

    # 下载图片
    def get_media_requests(self, item, info):
        try:
            imgs = item['article_imgs']
            if imgs != 'NULL':
                for img_url in imgs:
                    yield scrapy.Request(img_url)
        except:
            print item['article_imgs'], ":not image"

    # 图片重命名
    def item_completed(self, result, item, info):
        image_paths = [x['path'] for ok, x in result if ok]
        try:
            for path, img_url in zip(image_paths, item['article_imgs']):
                new_name = item['article_file_name'] + "/" + path.split('/')[-1]
                os.rename(path, new_name)
        except:
            print "image name error:", item['article_file_name']
            print "new_name:", new_name

        return item
