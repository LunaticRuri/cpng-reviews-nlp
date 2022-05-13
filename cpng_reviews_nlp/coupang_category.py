import json


class CoupangCategoryWriter:
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def to_dict(self):
        pass

    def to_json(self):
        pass


class CoupangCategoryReader:
    def __init__(self):
        pass

    def __repr__(self):
        pass


class CoupangCategory:

    def __init__(self, category_tree):
        self.category_tree = category_tree

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

    def fetch_reviews_data(self):
        # 새로 다운로드
        pass

    @classmethod
    def is_review_exists(cls):
        pass

    # 저장되어 있는 path에 조건에 맞는 파일이 있으면 로드 아니면 fetch_reviews_data
    def set_reviews_data(self):
        pass

    def get_target_category(self):
        pass

    def get_target_product_list(self):
        pass

    def get_reviews_data(self, product_list):
        pass
