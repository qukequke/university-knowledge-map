# from urllib.parse import quote
from urllib.parse import quote

import scrapy
import pandas as pd

df = pd.DataFrame()
from univer.items import UniverItem


class Spider1Spider(scrapy.Spider):
    name = 'spider1'
    allowed_domains = ['baike.baidu.com']
    df = pd.read_csv('university.csv')
    names = df['name'].tolist()
    names = [i for i in names if str(i)!='nan']
    # start_urls = [f"https://baike.baidu.com/search?word={quote(name)}" for name in names]
    # for name in names:
    #     print(name)
    #     print(quote(name))
    start_urls = [f"https://baike.baidu.com/search?word={quote(name)}" for name in names]
    print(start_urls)

    def parse(self, response):
        urls = response.xpath("//a[@class='result-title']/@href").extract()
        if urls:
            url = urls[0]
            yield scrapy.Request(url=url, callback=self.parse_2, dont_filter=True)

    def parse_2(self, response):
        rule1 = "//div[@class='basic-info J-basic-info cmn-clearfix']/dl/dt[@class='basicInfo-item name']"
        con = "//div[@class='basic-info J-basic-info cmn-clearfix']/dl/dd[@class='basicInfo-item value']"
        title = response.xpath(rule1)
        con = response.xpath(con)
        title = [i.xpath('string(.)').extract()[0].strip() for i in title]
        con = [i.xpath('string(.)').extract()[0].strip() for i in con]
        abstract = "//div[@class='para']"
        abstract = response.xpath(abstract).xpath('string(.)').extract()[0]
        a = UniverItem()
        dict_ = {i: j for i, j in zip(title, con)}
        dict_['desc'] = abstract
        a['name'] = dict_
        yield a
