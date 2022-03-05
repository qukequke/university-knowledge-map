#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

from template import semantic_slot
from util import logger


class QuestionPaser:
    def __init__(self, searcher):
        self.searcher = searcher
        # logger.info(self.searcher.g.run("MATCH (n:`内容`) RETURN n LIMIT 25").data())
        # self.g = searcher.g

    '''构建实体节点'''

    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''

    def parser_main(self, res_classify):
        args = res_classify['args']  # {'血肿（瘀斑）': ['A1类-以穿刺部位出血为主要表现的不良反应']}
        # entity_dict = self.build_entitydict(args)
        # logger.info(entity_dict)  # {'A1类-以穿刺部位出血为主要表现的不良反应': ['血肿（瘀斑）']}
        question_types = res_classify['question_types']
        sqls = []
        final_answer = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            for semantic_slot_one in semantic_slot:
                if question_type == semantic_slot_one['question_type']:
                    if not semantic_slot_one['slot_list']:
                        sql_list = [semantic_slot_one['sql'].format(f"m.name='{i}'") for i in args]

                    else:
                        if isinstance(semantic_slot_one['sql'], list):
                            sql_list = [sql.format(
                                f"({' or '.join([f'm:`{j}`' for j in semantic_slot_one['slot_list']])}) and m.name='{i}'")
                                for i in args for sql in semantic_slot_one['sql']]
                        else:
                            sql_list = [semantic_slot_one['sql'].format(
                                f"({' or '.join([f'm:`{j}`' for j in semantic_slot_one['slot_list']])}) and m.name='{i}'")
                                for i in args]

                    logger.info(f"解析后的sql 为 {sql_list}")
                    neo_data_list = [self.searcher.g.run(sql).data() for sql in sql_list]
                    neo_data_list = [i for i in neo_data_list if i]
                    # logger.info(f"得到neo4j_data为{neo_data_list}")

                    subject = semantic_slot_one['subject']
                    object_list = semantic_slot_one['object']
                    answer_list = [[semantic_slot_one['pretty'].format(data[subject], *data['object_list'])
                                    for data in [{subject: ''.join(set([i[subject] for i in neo_data])),
                                                  'object_list': ['、'.join(
                                                      [j[object_str] if isinstance(j[object_str], str) else '、'.join(
                                                          j[object_str])
                                                       for j in neo_data]) for object_str in object_list]
                                                  }]]
                                   for neo_data in neo_data_list]
                    answer_list = [i for i in answer_list if i]  # 不知道为何有空的字符串 需要去掉
                    # logger.info(answer_list)
                    answer = ' '.join([' '.join(i) for i in answer_list])
                    # logger.info(answer)
                    if answer:
                        final_answer.append(answer)
                    # logger.info(final_answer)
                    # logger.info(sql)
                    # sql = self.sql_transfer(question_type, entity_dict)
        return final_answer

    '''针对不同的问题，分开进行处理'''

    def sql_transfer(self, question_type, entities):
        if not entities:
            return []
        # 查询语句
        sql = []
        # 查询疾病的原因
        symptoms = list(entities.values())[0]
        label = list(entities.keys())[0]
        if question_type == 'symptom_cause':
            sql = [f"MATCH (m:`{label}`) where m.name = '{i}' return m.name, m.原因" for i in symptoms]

        # 反应包括哪些症状
        elif question_type == 'react_contain':
            sql = [f"MATCH (m:`{label}`)-[]->(n:`症状`) where m.name = '{i}' return m.name, n.name" for i in symptoms]

        return sql


if __name__ == '__main__':
    handler = QuestionPaser()
