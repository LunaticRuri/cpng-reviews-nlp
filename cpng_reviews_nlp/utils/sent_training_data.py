from konlpy.tag import Mecab
from jamo import h2j, j2hcj
from hangul_utils import join_jamos
import json
import re


class SimplePreprocessor:
    stop_pos = ['JX', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'EF', 'IC', 'VCP', 'VCN', 'XSN', 'MAJ',
                'VX', 'ETN', 'JC', 'EP', 'MM', 'NNBC', 'NP', 'EC', 'NMB', 'MAG', 'SY', 'SE', 'UNKNOWN']

    aspect_pos = ['NNP', 'NNG']

    desc_pos = ['VV', 'VA', 'VP']  # VP는 '이다, 아니다'가 붙어 서술어 역할을 하는 것

    stop_word = []

    pass_word = [['잘', 'MAG'], ['잘못', 'MAG']]

    def __init__(self):
        self.mecab = Mecab()

    @staticmethod
    def only_hangul_number_space_dot(raw_text):
        r_hangul = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s\d.]', "", raw_text)
        return r_hangul

    @staticmethod
    def pos_remover(token_pos_tuple_list):
        after_rm = []
        is_mag_an = False

        for elem in token_pos_tuple_list:

            target_pair = list(elem)

            if is_mag_an:
                target_pair[0] = '안_' + target_pair[0]

            is_etm = False
            is_mag_an = False

            if '+' in target_pair[1]:

                pos_stack = target_pair[1].split('+')

                if 'ETM' in pos_stack:
                    orig_jamo_str = j2hcj(h2j(target_pair[0]))[:-1]
                    target_pair[0] = join_jamos(orig_jamo_str)

                    is_etm = True

                if 'EC' in pos_stack:
                    # 대충 잘라 내기
                    if len(target_pair[0]) != 1:
                        target_pair[0] = target_pair[0][:-1]

                if 'XSV' in pos_stack:
                    try:
                        after_rm[-1][1] = 'VV'
                    except IndexError:
                        pass

                if 'XSA' in pos_stack:
                    try:
                        after_rm[-1][1] = 'VA'
                    except IndexError:
                        pass

                target_pair[1] = pos_stack[0]

                if target_pair[1] not in SimplePreprocessor.stop_pos or \
                        target_pair in SimplePreprocessor.pass_word:
                    if is_etm:
                        if target_pair[1] not in ['XSA', 'XSV']:
                            after_rm.append(target_pair)

                        after_rm.append(['*', 'ETM'])
                    else:
                        if target_pair[1] == 'ETM':
                            after_rm.append(['*', 'ETM'])
                        else:
                            if target_pair[1] not in ['XSA', 'XSV']:
                                after_rm.append(target_pair)



            else:
                if target_pair[1] == 'ETN':
                    try:
                        after_rm[-1][0] += target_pair[0]
                        after_rm[-1][1] = 'NNG'
                    except IndexError:
                        pass
                if target_pair[1] == 'XSV':
                    try:
                        after_rm[-1][1] = 'VV'
                    except IndexError:
                        pass

                if target_pair[1] == 'XSA':
                    try:
                        after_rm[-1][1] = 'VA'
                    except IndexError:
                        pass

                if target_pair[1] == 'XSN':
                    try:
                        after_rm[-1][0] += target_pair[0]
                    except IndexError:
                        pass

                if target_pair[1] == 'VCP':
                    try:
                        after_rm[-1][1] = 'VP'
                    except IndexError:
                        pass

                if target_pair[1] == 'VCN':
                    try:
                        after_rm[-1][1] = 'VP'
                        after_rm[-1][0] += '_아니'
                    except IndexError:
                        pass

                # 부정 부사 또는 보조 용언
                if target_pair == ['안', 'MAG']:
                    is_mag_an = True

                if target_pair == ['않', 'VX']:
                    try:
                        after_rm[-1][0] += '_않'
                    except IndexError:
                        pass
                if target_pair == ['못하', 'VX']:
                    try:
                        after_rm[-1][0] += '_못'
                    except IndexError:
                        pass

                if (target_pair[1] not in SimplePreprocessor.stop_pos and target_pair[1] not in ['XSA', 'XSV']) \
                        or target_pair in SimplePreprocessor.pass_word:
                    if target_pair[1] == 'ETM':
                        after_rm.append(['*', 'ETM'])
                    else:
                        after_rm.append(target_pair)

        after_rm.insert(0, ['', 'START'])
        after_rm.append(['', 'END'])

        return after_rm

    @staticmethod
    def remove_stop_word(token_pos_tuple_list):
        return [elem for elem in token_pos_tuple_list if elem not in SimplePreprocessor.stop_word]

    def preprocessing_str(self, pp_raw_text):
        target_text = self.only_hangul_number_space_dot(pp_raw_text)
        pos_list = self.pos_remover(self.mecab.pos(target_text))

        filtered_pos_list = self.remove_stop_word(pos_list)
        return ' '.join(str(e[0]) for e in filtered_pos_list)

    def preprocessing_tuple(self, pp_raw_text):
        target_text = self.only_hangul_number_space_dot(pp_raw_text)
        pos_list = self.pos_remover(self.mecab.pos(target_text))

        output_tuple_list = []
        history = []

        resv_indp = (False, ('', ''))

        for elem in pos_list:
            if elem == ['', 'START']:
                history.insert(0, elem)
            if elem[1] == 'SF':
                history = ['', 'START']
            elif elem[1] in SimplePreprocessor.aspect_pos or elem[1] == 'NNB':
                # ETM ~한
                if history[0][1] == 'ETM':
                    tmp_stack = [history[1][0]]
                    try:
                        if history[2][1] in SimplePreprocessor.aspect_pos:
                            tmp_stack.insert(0, history[2][0])
                    except IndexError:
                        pass
                    if elem[1] == 'NNB':
                        output_tuple_list.append(('', ' '.join(tmp_stack)))
                    else:
                        output_tuple_list.append((elem[0], ' '.join(tmp_stack)))

                if history[0][1] in SimplePreprocessor.aspect_pos:
                    output_tuple_list.append((history[0][0] + ' ' + elem[0], ''))

            elif elem[1] in SimplePreprocessor.desc_pos:
                if history[0][1] in SimplePreprocessor.aspect_pos:
                    try:
                        if history[1][1] in SimplePreprocessor.aspect_pos:
                            output_tuple_list.append((history[1][0] + ' ' + history[0][0], elem[0]))
                        else:
                            output_tuple_list.append((history[0][0], elem[0]))
                    except IndexError:
                        pass
                elif elem[1] == 'VA':
                    resv_indp = (True, ('', elem[0]))

            elif elem[1] != 'ETM' and resv_indp[0]:
                output_tuple_list.append(resv_indp[1])
                resv_indp = (False, ('', ''))

            else:
                pass

            if elem != ['', 'START']:
                history.insert(0, elem)

        return output_tuple_list


def test_simple_dependency_parser():
    sentence = "가장 저렴한 라면."

    dp = SimplePreprocessor()
    print(dp.preprocessing_tuple(sentence))


with open('../data/reviews/0abcdef.json') as fp:
    products = json.load(fp)

for elem in products.values():
    reviews = elem['reviews']

    positive_rv = ''
    negative_rv = ''

    for review in reviews:
        if review['rating'] in ['1', '2', '3']:
            negative_rv += review['data'] + '\n'
        else:
            positive_rv += review['data'] + '\n'

    min_len = min(len(positive_rv), len(negative_rv))
    if min_len < 2000:
        continue

    positive_min_rv = positive_rv[:min_len]
    negative_min_rv = negative_rv[:min_len]



