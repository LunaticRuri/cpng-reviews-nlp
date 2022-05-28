from konlpy.tag import Mecab
import re


class Preprocessor:
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
        if token_pos_tuple[1] == 'MAG' and token_pos_tuple[0] == '안':
            return False
        """

        if token_pos_tuple[1] in Preprocessor.stop_pos:
            return True
        else:
            return False

    @staticmethod
    def only_hangul_space(raw_text):
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


raw_sentence = \
    "실제로 사지 않았지만 딱 봐도 별로인 거 같네요."

pp =Preprocessor(mode=Preprocessor.POS)
print(pp.preprocessing(raw_sentence))
