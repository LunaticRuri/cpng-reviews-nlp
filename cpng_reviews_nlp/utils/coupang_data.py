"""
쿠팡 카테고리 데이터 다운로드 및 관리 모듈
사실 좀 구조적으로 만들려고 했는데 시간이 없어서 생각나는대로 만들었더니
원래 머릿속의 설계와는 많이 달라진 누더기 코드가 되어버렸다
경로 설정 주의가 필요
원래 여기서 리뷰까지 다 받아와서 한 오브젝트에서 다 처리할려고 했는데,
양이 너무 많아 run_dividing.py로 분할 실행했다.
"""

import json
from functools import reduce
from cpng_reviews_nlp.utils import coupang_reviews_fetcher as rf, coupang_category_fetcher as cf
import time
import os


class CoupangData:
    def __init__(
            self,
            root_category_id='all',
            max_product_count=200,
            max_char_count=20000,
            max_thread=40,
            category_file_path='../../data/backup/category_tree.json',
            reviews_file_path='../../data/reviews',
            category_update=False,
            get_reviews=False,
            reviews_update=False,
    ):
        """CoupangData 생성자
        :param root_category_id: 최상위 카테고리 - 자신을 제외한 하부 카테고리 모두 포함하게 됨
        all 이면 전체 카테고리.
        :type root_category_id: str
        :param max_product_count: 카테고리 당 최대 product 수
        :type max_product_count: int
        :param category_file_path: 카테고리 json 파일 저장할 경로, 디폴트는 '../../data/backup/category_tree.json'
        :type category_file_path: str
        :param reviews_file_path: 리뷰 json 파일 저장할 경로, 디폴트는 '../../data/reviews'
        :type category_file_path: str
        :param max_thread: 멀티쓰레딩에 사용할 최대 스레드 개수, 디폴트는 40
        :type max_thread: int
        :param category_update: True이면 파일 존재 여부와 관계 없이 데이터를 새로 받아옴
        :type category_update: bool
        """

        self.file_path = category_file_path
        self.root_category_id = root_category_id
        # 쿠팡이 카테고리 구조를 변경할 경우 파일과 불일치 문제로 에러 발생 가능 지점
        self.cwr = cf.CoupangCategoryFetcher(
            root_category_id,
            max_product_count,
            category_file_path,
            category_update,
            max_thread,
        )

        self.category_tree = self.cwr.get_category_tree()

        self.reviews_file_path = reviews_file_path

        if get_reviews:
            product_set = set()
            for _, v in self.get_all_category_iter(self.category_tree):
                if type(v) is list:
                    for elem in v:
                        product_set.add(elem)

            # TODO: 나중에 지우기
            # product_set=set(random.choices([*product_set], k=100))

            self.rwr = rf.CoupangReviewsFetcher(
                product_set,
                reviews_file_path,
                reviews_update,
                max_thread,
                max_char_count,
            )

            self.rwr.get_reviews()

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

    @staticmethod
    def get_all_category_iter(dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                yield key, value
                yield from CoupangData.get_all_category_iter(value)
            else:
                yield key, value

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

    def get_data_by_category(self, category_id):
        c_path = self.get_path(self.category_tree, category_id)
        data = self.get_values_by_path(c_path)
        return data

    def get_review_dict_from_file(self, product_id):
        try:
            with open(os.path.join(self.reviews_file_path, str(product_id) + '.json'), 'r', encoding="utf-8") as f:
                output_dict = json.load(f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            raise SystemExit("Can't find the file.")
        return output_dict


# Example Usage


def demo_coupang_category():
    test_tree = CoupangData(category_update=False)

    print(test_tree.is_exist('194282'))
    print(test_tree.get_parent('194282'))


def fetch_ramyeon_category():
    t1 = time.time()
    test_tree = CoupangData(
        category_update=True,
        root_category_id='486355',
        category_file_path='../ramyeon_category_tree.json',
    )
    count = 0
    for k, _ in CoupangData.get_all_category_iter(test_tree.get_category_tree()):
        if k.isdigit():
            count += 2
    print(count)
    t2 = time.time()
    print("time:", t2 - t1)


def fetch_ramyeon_reviews():
    t1 = time.time()
    test_tree = CoupangData(
        category_file_path="../ramyeon_category_tree.json",
        reviews_file_path="../data/tmp_reviews",
        category_update=False,
        get_reviews=True,
        reviews_update=False,
        max_product_count=400,
        max_char_count=40000,
    )
    print("soup_count: ", test_tree.rwr.get_soup_count())
    t2 = time.time()
    print("time:", t2 - t1)
