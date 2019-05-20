# -*- encoding:utf-8 -*- 
import urllib2


class YokaSpider:

	def request(self, url):

		header = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
		}

		return urllib2.urlopen(urllib2.Request(url=url, headers=header))


	def start_spider(self, url):
		response = self.request(url)
		print response.read()



if __name__ == '__main__':
	y = YokaSpider()
	y.start_spider("http://brandservice.yoka.com/v1/?_c=cmsbrandindex&_a=getCmsForZhuNew&_moduleId=29&channel=24&column=128&skip=44&limit=15&p=3")
