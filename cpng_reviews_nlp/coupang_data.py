import json
from functools import reduce
import pprint
from cpng_reviews_nlp import coupang_category_fetcher as cf
from cpng_reviews_nlp import coupang_reviews_fetcher as rf


class CoupangData:
    def __init__(
            self,
            root_category_id='all',
            max_product_count=200,
            file_path='./category_tree.json',
            max_thread=40,
            update=True,
    ):
        """CoupangData 생성자
        :param root_category_id: 최상위 카테고리 - 자신을 제외한 하부 카테고리 모두 포함하게 됨
        all 이면 전체 카테고리.
        :type root_category_id: str
        :param max_product_count: 카테고리 당 최대 product 수
        :type max_product_count: int
        :param file_path: 카테고리 json 파일 저장할 경로, 디폴트는 './category_tree.json'
        :type file_path: str
        :param max_thread: 멀티쓰레딩에 사용할 최대 스레드 개수, 디폴트는 40
        :type max_thread: int
        :param update: True이면 파일 존재 여부와 관계 없이 데이터를 새로 받아옴, 디폴트는 True
        :type update: bool
        """
        self.file_path = file_path
        self.root_category_id = root_category_id
        # 쿠팡이 카테고리 구조를 변경할 경우 파일과 불일치 문제로 에러 발생 가능 지점
        self.cwr = cf.CoupangCategoryFetcher(
            root_category_id,
            max_product_count,
            file_path,
            update,
            max_thread,
        )

        self.category_tree = self.cwr.get_category_tree()

        self.rwr = rf.CoupangReviewsFetcher()

    def __str__(self):
        tree_str = json.dumps(self.category_tree, indent=4, ensure_ascii=False)
        # json to str
        tree_str = tree_str.replace("\n    ", "\n")
        tree_str = tree_str.replace('"', "")
        tree_str = tree_str.replace(',', "")
        tree_str = tree_str.replace("{", "")
        tree_str = tree_str.replace("}", "")
        tree_str = tree_str.replace("    ", " | ")
        tree_str = tree_str.replace("  ", " ")

        return tree_str

    def __repr__(self):
        return str(self.category_tree)

    # TODO: staticmethods 여야 하는가?

    @staticmethod
    def get_path(target_dict, category_id, prepath=()):
        for k, v in target_dict.items():
            path = prepath + (k,)
            if k == category_id:  # found value
                return path
            elif type(v) is dict:  # v is a dict
                p = CoupangData.get_path(v, category_id, path)  # recursive call
                if p is not None:
                    return p

    def get_values_by_path(self, paths):
        return reduce(dict.get, paths, self.category_tree)

    def get_category_tree(self):
        return self.category_tree

    def is_exist(self, category_id):
        if str(self.category_tree).find(category_id) != -1:
            return True
        else:
            return False

    def get_parent(self, category_id):
        c_path = self.get_path(self.category_tree, category_id)
        try:
            parent = c_path[-3]
        except IndexError:
            return self.root_category_id

        return parent

    def get_children(self, category_id):
        if self.is_exist(category_id):
            children = self.get_values_by_path(self.get_path(self.category_tree, category_id))["children"]
            return children
        else:
            return False

    def get_data_by_id(self, category_id):
        c_path = self.get_path(self.category_tree, category_id)
        data = self.get_values_by_path(self.category_tree, c_path)
        return data


# Example Usage

def demo_coupang_category():
    test_tree = CoupangData(update=True)

    print(test_tree.is_exist('194282'))
    print(test_tree.get_parent('194282'))
    pprint.pprint(test_tree.get_children('194282'))
    pprint.pprint(test_tree.get_data_by_id('194282'))


def demo_coupang_reviews():
    test_tree = CoupangData('194282', update=True)
    count = 0
    for k, _ in cf.CoupangCategoryFetcher.get_all_category_iter(test_tree.get_category_tree()):
        if k.isdigit():
            count += 2
    print(count)


demo_coupang_reviews()
