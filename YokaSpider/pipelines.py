# -*- coding: utf-8 -*-


import scrapy

from scrapy.utils.project import get_project_settings
from scrapy.pipelines.images import ImagesPipeline

import os, hashlib


class YokaspiderPipeline(object):

    def process_item(self, item, spider):

        folder_name = item['article_file_name']

        file_name = item['article_title'] + '.txt'

        with open(folder_name + "/" + file_name, 'a')  as f:
            content = item['article_content']
            f.write(content.encode('utf-8') + '\n')

        img_info = folder_name + "/" + "img_info.txt"
        for name, url in zip(item['img_names'], item['article_imgs']):
            sha1_name = hashlib.sha1(url).hexdigest()
            info = name + " => " + sha1_name + " => " + url
            # print info
            with open(img_info, 'a') as f:
                f.write(info.encode('utf-8') + '\n')

        return item


class ImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for img_url in item['article_imgs']:
            yield scrapy.Request(img_url)

    def item_completed(self, result, item, info):
        image_paths = [x['path'] for ok, x in result if ok]

        for path in image_paths:
            new_name = item['article_file_name'] + "/" + path.split('/')[-1]
            # print "path:%s, new_name:%s" %(path, new_name)
            os.rename(path, new_name)

        return item
