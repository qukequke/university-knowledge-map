#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

import os
import ahocorasick
# from .config import semantic_slot
from util import logger
from config import object_name_list
from template import semantic_slot



class QuestionClassifier:
    def __init__(self, searcher):
        # self.g = searcher.g
        entity_dict = {i: searcher.get_all_object_name(i) for i in object_name_list}
        self.region_words = sum([list(i) for i in entity_dict.values()], [])
        print(self.region_words)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict(entity_dict)
        # print(self.region_words)
        # 问句疑问词
        print('model init finished ......')

        return

    def classify(self, question):
        """
        得到问题类型和相关实体
        """
        data = {}
        # print(question)
        medical_dict = self.check_medical(question)
        logger.info(f"找到实体为{medical_dict}")  # {'高血压': ['disease']
        # if not medical_dict:
        #     return {}
        data['args'] = medical_dict
        # 收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'

        question_types = []  # 同时验证了实体和关键词
        may_question_types = []  # 只验证关键词
        # print(semantic_slot)
        for semantic_slot_one in semantic_slot:
            # print(self.check_words(semantic_slot_one['keywords'], question))
            # print(set(semantic_slot_one['slot_list']) & set(types))
            if self.check_words(semantic_slot_one['keywords'], question) and (
                    (set(semantic_slot_one['slot_list']) & set(types)) or not semantic_slot_one['slot_list']):
                question_type = semantic_slot_one['question_type']
                question_types.append(question_type)
            # print(semantic_slot_one['keywords'])
            # print(question)
            # print()

            if self.check_words(semantic_slot_one['keywords'], question):
                may_question_type = semantic_slot_one['question_type']
                may_question_types.append(may_question_type)

        data['question_types'] = question_types
        data['may_question_types'] = may_question_types
        # data['question_label'] = question_label

        return data

    '''构造词对应的类型'''

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

    '''问句过滤'''

    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    from neo4j_helper import neo4j_handler

    handler = QuestionClassifier(neo4j_handler)
    while 1:
        # question = input('input an question:')
        # question = '溶血反应原因是什么'  # {'args': {'溶血反应': ['C类-单采血液成分相关不良反应']}, 'question_types': ['症状原因'], 'question_label': 'C类-单采血液成分相关不良反应'}
        # question = '献血不良反应分类指南起草人是谁'  # {'args': {'溶血反应': ['C类-单采血液成分相关不良反应']}, 'question_types': ['症状原因'], 'question_label': 'C类-单采血液成分相关不良反应'}
        # question = 'A1类-以穿刺部位出血为主要表现的不良反应症状有啥'  # {'args': {'溶血反应': ['C类-单采血液成分相关不良反应']}, 'question_types': ['症状原因'], 'question_label': 'C类-单采血液成分相关不良反应'}
        # question = '属于什么不良发音'
        # question = '昏厥属于什么'
        # question = '上呼吸道感染可以献血吗'
        question = '河北省有什么大学'
        data = handler.classify(question)
        print(data)
        break
