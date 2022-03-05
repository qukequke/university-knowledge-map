# -*- coding: utf-8 -*-
'''
---------------------------------------
@Time    : 2022/3/3 8:17
@Author  : quke
@File    : scrapy_2.py
@Description:
---------------------------------------
'''
import re

import requests
from lxml import etree
from pandas import DataFrame

url = "http://114.xixik.com/university/"

response = requests.get(url)
content = bytes(response.text, response.encoding).decode("gbk")

html = etree.HTML(content)
# td = "//div[@class='custom_content']/div[@class='content_text']/table/tbody/tr/td/text()"
tr = "//html/body/div[@class='body']/div[@class='custom_border lindBox'][1]/div[@class='custom_content']/div[@class='content_text']/table/tbody/tr"
d = html.xpath(tr)
d = ([[ii.strip() for ii in i.xpath('td/text()')] for i in d])
# print(d)
data = [{'num': i[0], 'name': i[1], 'code': i[2], 'management': i[3], 'city': i[4], 'class_1': i[5], 'class_2': i[6]}
        for i in d if len(i) == 7]
# print(data)
df = DataFrame(data)
df.to_csv("data/raw_table.csv", index=False)
rule2 = """/html/body/div[@class='body']/div[@class='custom_border lindBox'][2]/div[@class='custom_content']/
div[@class='content_text']/table/tbody/tr/td/text()"""
r = html.xpath(rule2)
r = [i.strip() for i in r][2:]
from collections import defaultdict

dict_ = defaultdict(list)
pre = r[0]
for i in r:
    if re.match('.+（\d+所）', i):
        pre = i
    else:
        dict_[pre].append(i)
# print(dict_.values())
# all_names = [i['name'] for i in r]
university_211 = sum(list(dict_.values()), [])
university_211 = [i for i in university_211 if i.strip()]
print(university_211)
# print(all_names)
# assert len(all_names) == len(set(all_names))
# print(set(university_211) - set(all_names))
dict_name2code = {i: j for i, j in zip(df['name'], df['code'])}
print(dict_name2code)

# university_985 =
# name2code_add = {'华北电力大学（保定）': 10079,
#                  '第二军医大学': 90026,
#                  '国防科学技术大学': 91002,
#                  '华北电力大学（北京）': 10054,
#                  '第四军医大学': 1,
#                  '西北农林科大': 4161010712,
#                  '中国矿业大学（徐州）': 10290
#                  }
# print(r)
# d = [i.strip() for i in d][4:]
# print(d)
# print(len(d)/5)
