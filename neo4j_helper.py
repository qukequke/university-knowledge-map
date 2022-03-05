from py2neo import Graph
from config import neo4j_support_url, object_name_list
import ahocorasick


class AnswerSearcher:
    def __init__(self, neo4j_support_url):
        # print(neo4j_support_url)
        self.g = Graph(
            host=neo4j_support_url['host'],
            port=neo4j_support_url['port'],
            user=neo4j_support_url['user'],
            password=neo4j_support_url['password']
        )
        self.num_limit = 20
        # self.entity_type = set(sum([i['labels(n)'] for i in entity_type], []))  # 库里的所有实体类型
        sql = "match(n)  return distinct n.name, labels(n)"
        sql_data = self.g.run(sql).data()
        # print(sql_data)
        self.entity_label_dict = {i['n.name']: i['labels(n)'][0] for i in sql_data if i['labels(n)']}
        self.entity_names = list(self.entity_label_dict.keys())
        labels_pre = list(self.entity_label_dict.values())
        self.labels = list(set(labels_pre))
        self.labels.sort(key=labels_pre.index)
        # entity_dict = {i: self.get_all_object_name(i) for i in object_name_list}
        entity_dict = {i: self.get_all_object_name(i) for i in self.labels}  # 改成所有标签
        self.region_words = sum([list(i) for i in entity_dict.values()], [])
        # print(self.region_words)
        self.region_tree = self.build_actree(list(self.region_words))
        self.wdtype_dict = self.build_wdtype_dict(entity_dict)

    def build_wdtype_dict(self, entity_dict):
        wd_dict = {}
        for k, v in entity_dict.items():
            for i, v_one in enumerate(v):
                if v_one not in wd_dict:
                    wd_dict[v_one] = [k, ]
                else:
                    wd_dict[v_one].append(k)
        return wd_dict

    '''构造actree，加速过滤'''

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            if not word:
                continue
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []  # 白菜和瓜烧白菜  去掉白菜
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    def print_kg(self):
        sql_keys = "MATCH (n:Disease) return keys(n)"
        sql = "match(n) return distinct labels(n)"
        entity_type = self.g.run(sql).data()
        entity_type = set(sum([i['labels(n)'] for i in entity_type], []))
        # entity_type = [i.get('labels(n)')[0] for i in entity_type if i.get('labels(n)')]
        print('共有' + str(len(entity_type)) + '种实体类型')
        print(entity_type)
        for entity_type_one in entity_type:
            data = self.g.run(f"match (n:`{entity_type_one}`) return count(n)").data()
            property = self.g.run(f"match (n:`{entity_type_one}`) return n").data()
            property = [i.get('n').keys() for i in property]
            # print(property)
            new_property = set()
            for i in property:
                # print(i)
                new_property = new_property | i
            property = new_property
            propertys = ', '.join(property)
            nums_entity = data[0].get('count(n)')
            print(f'{entity_type_one}({nums_entity}) 具有{len(property)}种属性, 分别为{propertys}')

        rel_sql = "match (n)-[r]->(m) return distinct type(r)"
        rel_types = self.g.run(rel_sql).data()
        rel_types = [i.get('type(r)') for i in rel_types]
        print('\n')
        print('共有' + str(len(rel_types)) + '种关系')
        edges = []
        for rel_type_one in rel_types:
            data = (
                self.g.run(f"match (n)-[r:{rel_type_one}]->(m) return count(r), r.name, labels(m), labels(n)").data())
            nums = data[0].get('count(r)')
            name = data[0].get('r.name')
            labels_m = data[0].get('labels(m)')[0]
            labels_n = data[0].get('labels(n)')[0]
            edges.append([labels_m, labels_n, nums])
            print(f'{labels_m}-{rel_type_one}({name})-{labels_n} 总数目为{nums}')
        # print(edges)
        edges = [[i[0], i[1]] for i in edges]
        # draw_pic(edges)

    '''分类主函数'''

    def get_all_object_name(self, object_name):
        # sql = "match(n) where n.nodeType=1 or n.nodeType=4 return distinct n.name, labels(n)"
        sql = "match (n:`{}`) return n.name".format(object_name)
        ret = self.g.run(sql).data()
        objects = [i.get('n.name') for i in ret]
        return objects

    # @staticmethod
    # def gen_blood_question(self):
    #     """
    #     通过模板产生血液问题
    #     """
    #     symptoms = self.get_all_object_name('症状')
    #     belong_kws = ['属于什么分类']
    #     a = ['什么时候发布的呢']
    # def pinyin_dict(self):
    #    from pinyin import pinyin


neo4j_handler = AnswerSearcher(neo4j_support_url)

if __name__ == '__main__':
    # neo4j_handler.print_kg()
    neo4j_handler = AnswerSearcher(neo4j_support_url)
    # neo4j_handler.
    d = neo4j_handler.g.run('MATCH (n) where n.nodeType=1 RETURN n.name').data()
    names = [i['n.name'] for i in d]
    file_name = 'data/neo4j_user_dict.txt'
    names = [i for i in names if len(i) <= 10]
    with open(file_name, 'w', encoding='utf-8') as f:
        f.writelines([i+'\n' for i in names])


    # d = neo4j_handler.g.run("MATCH (m)<-[r:`暂不能献血`]-(n) where  m.name='纹身术' RETURN m.name, COALESCE(r.状态, '') as r_状态, r.暂缓时间").data()
    # print(d)
