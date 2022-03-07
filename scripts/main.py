import json

import pandas as pd
import re


def dis(str_):
    str_ = str_.replace('\xa0', '')
    str_ = re.subn('\[\d+\]', '', str_)[0].strip()
    str_ = str_.replace('\n', '').replace("'", "\\'")
    # if "'" in str_:
    #     print(str_)
    return str_


def get_df():
    file_name = 'data/xiaoshuo.json'
    with open(file_name, 'r', encoding='utf-8') as f:
        d = json.load(f)
    data = ([i['name'] for i in d])
    data = [{dis(k): dis(v) for k, v in dict_.items()} for dict_ in data]
    df = pd.DataFrame(data)
    df['简称_2'] = df['简称'].apply(lambda x:(re.split('[（、，·]', x.rstrip('）'))) if not pd.isna(x) else [])
    return df


# df.to_csv('a.csv', index=False, encoding='utf-8')

def create_university(df, g):
    for index, row in df.iterrows():
        # print(row.index)
        # for i in row.index:
        #     print(row[i])
        row = row.dropna()
        d = [f"`{i}`:'{row[i]}'" for i in row.index]
        # print(d)
        # print(type(row))
        sql = f"CREATE (n:`大学`{{{','.join(d)}}}) return n;"
        print(sql)
        g.run(sql)
        list_ = row['简称_2']
        if '中文名' in row:
            for name in list_:
                sql = f"CREATE (n:`大学简称`{{name:'{name}'}}) return n;"
                print(sql)
                g.run(sql)
                sql = f"match (m:`大学`), (n:`大学简称`) where m.name='{row['中文名']}' and n.name='{name}' create (m)-[:`简称`]->(n)"
                g.run(sql)
                print(sql)

        # break


def city_save(g):
    """
    省市关系建立
    """
    file_name = 'data/pc-code.json'
    with open(file_name, 'r', encoding='utf-8') as f:
        d = json.load(f)
    # print(d)
    data = [[i['name'], ii['name']] for i in d for ii in i['children']]
    print(data)
    all_node = set(sum(data, []))
    for node in all_node:
        sql = f"create (n:`城市`{{name:'{node}'}})"
        g.run(sql)
    for i, j in data:
        sql = f"match (m), (n) where m.name='{i}' and n.name='{j}' create (m)-[:`包含`]->(n)"
        g.run(sql)


def create_univer_city(g):
    df = pd.read_csv('data/raw_table.csv', encoding='gbk')
    for i in set(df['management'].tolist()):
        sql = f"create (n:`主管单位`{{name:'{i}'}})"
        print(sql)
        # g.run(sql)
    for index, row in df.iterrows():
        sql = f"match (m:`大学`) where m.name='{row['name']}' set m.`类型`='{row['class_1']}', m.code={row['code']}"
        g.run(sql)
        print(sql)
        sql = f"match (m), (n) where m.name='{row['name']}' and n.name='{row['city']}' create (m)-[:`位于`]->(n)"
        g.run(sql)
        print(sql)
        sql = f"match (m), (n:`主管单位`) where m.name='{row['name']}' and n.name='{row['city']}' create (m)-[:`主管单位`]->(n)"
        g.run(sql)
        print(sql)


def get_detail(df):
    university_985 = ['清华大学', '北京大学', '厦门大学', '南京大学', '复旦大学', '天津大学',
                      '浙江大学', '南开大学', '西安交通大学', '东南大学', '武汉大学', '上海交通大学', '山东大学', '湖南大学',
                      '中国人民大学', '吉林大学', '重庆大学', '电子科技大学', '四川大学', '中山大学', '华南理工大学', '兰州大学',
                      '东北大学', '西北工业大学', '哈尔滨工业大学', '华中科技大学', '中国海洋大学', '北京理工大学', '大连理工大学',
                      '北京航空航天大学', '北京师范大学', '同济大学', '中南大学', '中国科学技术大学', '中国农业大学', '国防科学技术大学', '中央民族大学',
                      '华东师范大学', '西北农林科技大学', ]
    university_211 = ['清华大学', '北京大学', '中国人民大学', '北京工业大学', '北京理工大学', '北京航空航天大学', '北京化工大学', '北京邮电大学', '对外经济贸易大学',
                      '中国传媒大学', '中央民族大学', '中国矿业大学（北京）', '中央财经大学', '中国政法大学', '中国石油大学（北京）', '中央音乐学院', '北京体育大学', '北京外国语大学',
                      '北京交通大学', '北京科技大学', '北京林业大学', '中国农业大学', '北京中医药大学', '华北电力大学（北京）', '北京师范大学', '中国地质大学（北京）', '复旦大学',
                      '华东师范大学', '上海外国语大学', '上海大学', '同济大学', '华东理工大学', '东华大学', '上海财经大学', '上海交通大学', '南开大学', '天津大学',
                      '天津医科大学', '重庆大学', '西南大学', '华北电力大学（保定）', '河北工业大学', '太原理工大学', '内蒙古大学', '大连理工大学', '东北大学', '辽宁大学',
                      '大连海事大学', '吉林大学', '东北师范大学', '延边大学', '东北农业大学', '东北林业大学', '哈尔滨工业大学', '哈尔滨工程大学', '南京大学', '东南大学',
                      '苏州大学', '河海大学', '中国药科大学', '中国矿业大学（徐州）', '南京师范大学', '南京理工大学', '南京航空航天大学', '江南大学', '南京农业大学', '浙江大学',
                      '安徽大学', '合肥工业大学', '中国科学技术大学', '厦门大学', '福州大学', '南昌大学', '山东大学', '中国海洋大学', '中国石油大学（华东）', '郑州大学',
                      '武汉大学', '华中科技大学', '中国地质大学（武汉）', '华中师范大学', '华中农业大学', '中南财经政法大学', '武汉理工大学', '湖南大学', '中南大学',
                      '湖南师范大学', '中山大学', '暨南大学', '华南理工大学', '华南师范大学', '广西大学', '四川大学', '西南交通大学', '电子科技大学', '西南财经大学',
                      '四川农业大学', '云南大学', '贵州大学', '西北大学', '西安交通大学', '西北工业大学', '陕西师范大学', '西北农林科大', '西安电子科技大学', '长安大学',
                      '兰州大学', '新疆大学', '石河子大学', '海南大学', '宁夏大学', '青海大学', '西藏大学', '第二军医大学', '第四军医大学', '国防科学技术大学']
    university_yiliu = [
        "北京大学", "中国人民大学", "清华大学", "北京航空航天大学", "北京理工大学",
        "中国农业大学", "北京师范大学", "中央民族大学", "南开大学", "天津大学",
        "大连理工大学", "吉林大学", "哈尔滨工业大学", "复旦大学", "同济大学",
        "上海交通大学", "华东师范大学", "南京大学", "东南大学", "浙江大学",
        "中国科学技术大学", "厦门大学", "山东大学", "中国海洋大学", "武汉大学",
        "华中科技大学", "中南大学", "中山大学", "华南理工大学", "四川大学",
        "重庆大学", "电子科技大学", "西安交通大学", "西北工业大学", "兰州大学",
        "国防科技大学",
        "东北大学", "郑州大学", "湖南大学", "云南大学", "西北农林科技大学",
        "新疆大学",
        "北京交通大学", "北京工业大学", "北京科技大学", "北京化工大学", "北京邮电大学",
        "北京林业大学", "北京协和医学院", "北京中医药大学", "首都师范大学", "北京外国语大学",
        "中国传媒大学", "中央财经大学", "对外经济贸易大学", "外交学院", "中国人民公安大学",
        "北京体育大学", "中央音乐学院", "中国音乐学院", "中央美术学院", "中央戏剧学院",
        "中国政法大学", "天津工业大学", "天津医科大学", "天津中医药大学", "华北电力大学",
        "河北工业大学", "太原理工大学", "内蒙古大学", "辽宁大学", "大连海事大学",
        "延边大学", "东北师范大学", "哈尔滨工程大学", "东北农业大学", "东北林业大学",
        "华东理工大学", "东华大学", "上海海洋大学", "上海中医药大学", "上海外国语大学",
        "上海财经大学", "上海体育学院", "上海音乐学院", "上海大学", "苏州大学",
        "南京航空航天大学", "南京理工大学", "中国矿业大学", "南京邮电大学", "河海大学",
        "江南大学", "南京林业大学", "南京信息工程大学", "南京农业大学", "南京中医药大学",
        "中国药科大学", "南京师范大学", "中国美术学院", "安徽大学", "合肥工业大学",
        "福州大学", "南昌大学", "河南大学", "中国地质大学", "武汉理工大学",
        "华中农业大学", "华中师范大学", "中南财经政法大学", "湖南师范大学", "暨南大学",
        "广州中医药大学", "华南师范大学", "海南大学", "广西大学", "西南交通大学",
        "西南石油大学", "成都理工大学", "四川农业大学", "成都中医药大学", "西南大学",
        "西南财经大学", "贵州大学", "西藏大学", "西北大学", "西安电子科技大学",
        "长安大学", "陕西师范大学", "青海大学", "宁夏大学", "石河子大学",
        "中国石油大学", "宁波大学", "中国科学院大学", "第二军医大学", "第四军医大学",
    ]

    df['双一流'] = df['中文名'].apply(lambda x: x in university_yiliu)
    df['211'] = df['中文名'].apply(lambda x: x in university_211)
    df['985'] = df['中文名'].apply(lambda x: x in university_985)
    print(df['双一流'].value_counts())
    print(df['211'].value_counts())
    print(df['985'].value_counts())

    for name in ['双一流', '211', '985']:
        sql = f"create (n:`学校层次`{{name:'{name}'}})"
        print(sql)
        g.run(sql)
    for index, row in df.iterrows():
        for name in ['双一流', '211', '985']:
            if row[name]:
                sql = f"match (m), (n) where m.name='{row['中文名']}' and n.name='{name}' create (m)-[:`属于`]->(n)"
                print(sql)
                g.run(sql)


if __name__ == '__main__':
    from py2neo import Graph
    # from config import neo4j_support_url

    neo4j_support_url = {
        # 'host': 'xx.xx.xx.xx',
        'host': '106.14.140.139',
        'port': 7687,
        'user': 'neo4j',
        'password': 'password',
    }
    g = Graph(
        host=neo4j_support_url['host'],
        port=neo4j_support_url['port'],
        user=neo4j_support_url['user'],
        password=neo4j_support_url['password']
    )
    df = get_df()
    create_university(df, g)  # 创建大学实体
    # city_save(g)  # 城市
    # create_univer_city(g)  # 大学和城市建立关系
    # get_detail(df)  # 211 985加入
