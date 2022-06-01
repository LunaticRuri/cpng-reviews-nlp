from konlpy.tag import Mecab


class SimpleDependencyParser:

    stop_pos = ['JX', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'EF',
                'JC', 'SY', 'EP', 'MM', 'NNBC', 'NP', 'EC', 'VCP', 'NMB', 'MAG']

    def __init__(self):
        self.mecab = Mecab()

    @staticmethod
    def pos_remover(token_pos_tuple_list):
        output_list = [elem for elem in token_pos_tuple_list if elem[1] not in SimpleDependencyParser.stop_pos]
        return output_list

    def foo(self, pp_raw_text):
        raw_pos_list = self.mecab.pos(pp_raw_text)
        print(SimpleDependencyParser.pos_remover(raw_pos_list))

    def bar(self):
        pass


def test_simple_dependency_parser():
    sentence = "아침에 깬다음 피곤해서 더 자는 일이 줄어드는 느낌입니다."
    dp = SimpleDependencyParser()
    dp.foo(sentence)


test_simple_dependency_parser()
