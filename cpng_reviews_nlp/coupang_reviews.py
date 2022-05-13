
class CoupangReviewsWriter:
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def to_dict(self):
        pass

    def to_json(self):
        pass


class CoupangReviewsReader:
    def __init__(self):
        pass

    def __repr__(self):
        pass


class CoupangReviews:

    def __init__(self):
        # init 에서 타겟 카테고리 설정
        pass

    def __repr__(self):
        pass

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
