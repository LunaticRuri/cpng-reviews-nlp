"""
간단한 전처리기
"""

from konlpy.tag import Mecab
import re


class Preprocessor:
    # 제외 목록
    stop_pos = ['JX', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'EF',
                'JC', 'SY', 'EP', 'MM', 'NNBC', 'NP', 'EC', 'VCP', 'NMB', 'MAG']

    POS = "pos"
    MORPHS = "morphs"

    def __init__(self, mode):
        self.mecab = Mecab()

        if mode == Preprocessor.POS:
            self.mode = Preprocessor.POS
        else:
            self.mode = Preprocessor.MORPHS

    @staticmethod
    def pos_remover(token_pos_tuple):
        """

        :param token_pos_tuple: ()
        :return:
        """
        if token_pos_tuple[1] in Preprocessor.stop_pos:
            return True
        else:
            return False

    @staticmethod
    def only_hangul_number_space(raw_text):
        r_hangul = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s\d]', "", raw_text)
        return r_hangul

    @staticmethod
    def pos_to_morphs(pos_list):
        output_list = [elem[0] for elem in pos_list]
        return output_list

    def preprocessing(self, raw_text):
        hangul = self.only_hangul_space(raw_text)
        pos_list = self.mecab.pos(hangul)
        output_list = [elem for elem in pos_list if not self.pos_remover(elem)]

        if self.mode == Preprocessor.MORPHS:
            output_list = self.pos_to_morphs(output_list)

        return output_list


def test_preprocessor_pos(raw_sentence):
    pp = Preprocessor(mode=Preprocessor.POS)
    print(pp.preprocessing(raw_sentence))
