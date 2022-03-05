from question_classifier import *
from question_parser import *
from neo4j_helper import AnswerSearcher
from config import neo4j_support_url
from collections import defaultdict

user_session_dict = defaultdict(dict)


'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.searcher = AnswerSearcher(neo4j_support_url)
        self.classifier = QuestionClassifier(self.searcher)
        self.parser = QuestionPaser(self.searcher)

    def chat_main(self, sent, user, CLEAR_USER_SESSION_ROUND=3):
        global user_session_dict
        session_dict = user_session_dict[user]
        answer = ''
        res_classify = self.classifier.classify(sent)
        logger.info(f"问题分类结果为{res_classify}")
        # {'args': {'溶血反应': ['C类-单采血液成分相关不良反应']}, 'question_types': ['不良反应反应包含症状']}
        cache_slot_values = session_dict.get('slot_values', {})
        cache_user_intent = session_dict.get('user_intent', '')
        cache_count = session_dict.get('qa_count', 0)
        # if cache_count >= CLEAR_USER_SESSION_ROUND:
        #     logger.info('清空用户状态')
        #     session_dict.clear()
        # else:
        #     session_dict['qa_count'] = cache_count + 1
        #     if res_classify.get('may_question_types', {}) and not res_classify['args']:  # 有意图没实体，槽位继承
        #         logger.info('槽位继承')
        #         res_classify['args'] = {v: [k, ] for k, v in cache_slot_values.items()}  # 继承槽位
        #         res_classify['question_types'] = res_classify['may_question_types']
        #     elif not res_classify.get('may_question_types') and res_classify['args']:  # 有实体没意图，意图继承
        #         logger.info('意图继承')
        #         res_classify['question_types'] = cache_user_intent
        logger.info(f"整合后的结果为{res_classify}")
        slot_list = sum((res_classify['args'].values()), [])
        session_dict['slot_list'] = slot_list
        session_dict['slot_values'] = {v[0]: k for k, v in res_classify['args'].items()}
        session_dict['user_intent'] = res_classify['question_types']
        logger.info(session_dict)
        # logger.info(user_session_dict)
        # logger.info(f'user_session_dict内部为{user_session_dict}')
        print(res_classify)
        if not res_classify:
            return answer, ''
        final_answers = self.parser.parser_main(res_classify)
        if not final_answers:
            return answer, ''
        else:
            return '\n'.join(final_answers), res_classify['question_types']


if __name__ == '__main__':
    # global user_session_dict
    user_session_dict = {'123': {}}
    handler = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question, '123')
        logger.info(f'小勇:{answer[0]}')
