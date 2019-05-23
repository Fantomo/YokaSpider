# -*- coding: utf-8 -*-
import scrapy
from YokaSpider.items import YokaspiderItem

import os, re
import urllib, json


class YokaSpider(scrapy.Spider):
	name = 'yoka'
	allowed_domains = ['yoka.com']
	start_urls = ['http://beauty.yoka.com/']

	# 匹配图集url
	pattern = re.compile(r"/pic\d+.shtml$")

	def parse(self, response):

		items = []

		# 美容下的所有子类
		sub_urls = response.xpath("//div[@class='twoNav']/div/a/@href").extract()
		sub_titles = response.xpath("//div[@class='twoNav']/div/a/text()").extract()

		start_url = 'http://www.yoka.com/beauty/'

		for sub_url, sub_title in zip(sub_urls, sub_titles):

			if sub_url.startswith(start_url) and not sub_url.endswith('/homme/'):
				item = YokaspiderItem()
				# 子类目录
				sub_file_name = "./data/" + sub_title

				# 创建目录
				if not os.path.exists(sub_file_name):
					os.makedirs(sub_file_name)

				item['sub_title'] = sub_title
				item['sub_url'] = sub_url
				item['sub_file_name'] = sub_file_name

				items.append(item)

		for item in items:
			yield scrapy.Request(url=item['sub_url'], meta={'data': item}, callback=self.second_parse)

	# 抓取指定
	def second_parse(self, response):

		meta_data = response.meta['data']

		# 文章 url 标题
		article_urls, article_titles = self.get_article(response)

		items = []

		# 爬取页面 文章url, 文章title
		for url, title in zip(article_urls, article_titles):

			if url.startswith(meta_data['sub_url']) and url.endswith(".shtml"):
				item = YokaspiderItem()
				# 文章目录
				article_file_name = meta_data['sub_file_name'] + "/" + title

				# 创建文章文件夹
				if not os.path.exists(article_file_name):
					os.makedirs(article_file_name)

				# 保存文章 url, title, filename
				item['sub_title'] = meta_data['sub_title']
				item['sub_url'] = meta_data['sub_url']
				item['sub_file_name'] = meta_data['sub_file_name']
				item['article_url'] = url
				item['article_file_name'] = article_file_name

				items.append(item)
		for item in items:
			yield scrapy.Request(item['article_url'], meta={'data': item}, callback=self.article_parse)

		# ajax 数据 
		# === begin ===
		response_url = response.url
		follow = True
		column = 0
		page = 1
		skip = 44

		while follow:
			item = {}
			ajax_url = "http://brandservice.yoka.com/v1/?"

			form_data = {
				"_c":"cmsbrandindex",
				"_a":"getCmsForZhuNew",
				"_moduleId":"29",
				"channel":"24",
				"column":column,
				"skip":skip,
				"limit":"15",
				"p":page,
			}

			if response_url.endswith("/skincare/"):  # 护肤前沿
				column = 128
			elif response_url.endswith("/fragrance/"):  # 彩妆香氛
				column = 274
			elif response_url.endswith("/bodycare/"):  # 美发美体
				column = 273
			elif response_url.endswith("/news/"):  # 美丽新鲜事
				column = 115
				skip = 45

			data = urllib.urlencode(form_data)

			# 美容子类 url, title, filename
			item['sub_title'] = meta_data['sub_title']
			item['sub_url'] = meta_data['sub_url']
			item['sub_file_name'] = meta_data['sub_file_name']

			# 请求url
			full_url = ajax_url + data
			yield scrapy.Request(full_url, meta={'data':item}, callback=self.ajax_pase)


			page += 1
			if page > 10:
				follow = False

		# === finish ===

	# ajax 数据解析
	def ajax_pase(self, response):

		items = []

		meta_data = response.meta['data']


		response = json.loads(response.body, encoding='gbk')
		for context in response['context']:
			item = YokaspiderItem()
			article_url = context['link']
			article_title = self.check_char(context['title'])

			if not self.pattern.search(article_url):

				# 文章目录
				article_file_name = meta_data['sub_file_name'] + "/" + article_title

				# 创建文章目录
				if not os.path.exists(article_file_name):
					os.makedirs(article_file_name)

				item['sub_title'] = meta_data['sub_title']
				item['sub_url'] = meta_data['sub_url']
				item['sub_file_name'] = meta_data['sub_file_name']
				item['article_url'] = article_url
				item['article_file_name'] = article_file_name

				items.append(item)

		for item in items:
			yield scrapy.Request(url=item['article_url'], meta={'data': item}, callback=self.article_parse)


	# 文章解析
	def article_parse(self, response):

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

		# 判断是否需要跟进
		next_page = self.get_next_page(response)
		if next_page:
			next_page_url = "http://www.yoka.com" + next_page
			yield scrapy.Request(url=next_page_url, meta={"data": item}, callback=self.article_parse)
		else:
			pass

		yield item

	# 文章标题
	def get_article_title(self, response):
		article_title = response.xpath("//div[@class='gLeft']/h1/text()").extract()
		if len(article_title):
			article_title = article_title[0]
			article_title = self.check_char(article_title)
		else:
			article_title = 'NULL'
		return article_title

	# 文章内容
	def get_article_content(self, response):
		content = response.xpath("//div[@class='textCon']/p")
		article_content = content.xpath("./text() | ./span/text() | ./strong/text() | ./span/strong/text()").extract()
		if len(article_content):
			article_content = "".join(article_content).strip().replace("\t", "").\
				replace("\n\n\t", "\n").replace("\n\n\n", "\n").replace("\n\n", "\n").\
				replace("\n\n\n\n", "\n").replace("\n \n  \n  \n  \n", "\n")
		else:
			article_content = 'NULL'
		return article_content

	# 摘要
	def get_article_quote(self, response):
		article_quote = response.xpath("//div[@class='double_quotes']/div/text()").extract()
		if len(article_quote):
			article_quote = article_quote[0]
		else:
			article_quote = 'NULL'
		return article_quote

	# 标签
	def get_article_tag(self, response):
		article_tag = response.xpath("//div[@class='navTag']/a/text()").extract()
		if len(article_tag):
			article_tag = " ".join(article_tag)
		else:
			article_tag = 'NULL'
		return article_tag

	# 图片url
	def get_article_imgs(self, response):
		article_imgs = response.xpath("//div[@class='editer_pic']//img/@src").extract()
		if len(article_imgs):
			article_imgs = article_imgs
		else:
			article_imgs = 'NULL'
		return article_imgs

	# 图片名
	def get_img_names(self, response):
		img_names = response.xpath("//div[@class='editer_pic']/i/text()").extract()
		img_title = response.xpath("//div[@class='editer_pic']//img/@alt").extract()
		if len(img_names):
			img_names = img_names
		elif len(img_title):
			img_names = img_title
		else:
			img_names = 'NULL'
		return img_names

	# 下一页
	def get_next_page(self, response):
		next_page = response.xpath("//div[@class='pages']/a[@class='next']/@href").extract()
		if next_page:
			next_page = next_page[0]
		else:
			next_page = False
		return next_page

	# 获取文章title, url
	def get_article(self, response):
		article_urls = response.xpath("//div[@class='tit']/a/@href").extract()
		article_titles = response.xpath("//div[@class='tit']/a/text()").extract()
		titles = []
		urls = []

		for url, title in zip(article_urls, article_titles):
			if not self.pattern.search(url):
				title = self.check_char(title)
				urls.append(url)
				titles.append(title)

		return urls, titles

	# 修改字符串中的特殊符号
	def check_char(self, title):
		if u'\u200b' in title:  # '\u200b' &#8203; 零宽空格
			title = title.replace(u'\u200b', '')
		elif '&#8203;' in title:
			title = title.replace('&#8203;', '')
		elif u'\xd4' in title:  # '\xd4' Ô
			title = title.replace(u'\xd4', '_')
		elif '&#212;' in title:
			title = title.replace('&#212;', '_')
		elif u'\u2022' in title: # '\u2022' &#8226; •
			title = title.replace(u'\u2022', '_')
		elif '&#8226;' in title:
			title = title.replace('&#8226;', '_')
		elif '"' in title:
			title = title.replace('"', '_')
		elif '?' in title:
			title = title.replace('?', '_')
		elif '=' in title:
			title = title.replace('=', '_')
		elif '+' in title:
			title = title.replace('+', '_')
		elif '&#8482;' in title:  # &#8482;  ™
			title = title.replace('&#8482;', '_')
		elif '\\' in title:
			title = title.replace('\\', '_')
		elif '...' in title:
			title = title.replace('...', '')
		else:
			title = title.replace(' ', '')
		return title
