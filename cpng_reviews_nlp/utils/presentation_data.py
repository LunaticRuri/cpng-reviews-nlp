"""
발표 자료 및 보고서용 데이터 산출 목적 코드
"""

import json

"""
리뷰 데이터 설명

쿠팡의 메인 카테고리와 그 세부 카테고리 판매량 상위 200개 상품 대상
리뷰는 20000자 이상이 넘지 않게 설정

0: 170000 a: 97362 b: 97833 c:97833 d: 97833 e:97833 f:97832 = 756256
모든 별점 별로 8000개 이상 컷, 모든 별점 리뷰 합해서 10000자 이상
total -> 17631
4,5점 별점 별로 10000자 이상, 4,5점 리뷰만 합해서 10000자 이상
45 -> 16634
1,2,3점 별점 별로 2000자 이상, 1,2,3점 리뷰만 합해서 2000자 이상
낮은 별점 데이터는 비중이 작아서 기준을 달리할 수밖에 없었다
123 -> 15537
"""

"""
카테고리별 리뷰 분포 확인
여성패션 9896
남성패션 7028
남녀 공용 의류 796
유아동패션 5907
뷰티 11263
출산/유아동 30059
식품 46009
주방용품 21944
생활용품 20387
홈인테리어 28799
가전디지털 20027
스포츠/레저 24206
자동차용품 9249
도서/음반/DVD 22668
완구/취미 23271
문구/오피스 17999
반려동물용품 2126
헬스/건강식품 24356
"""


reviews_path = "../../data/reviews/0abcdef.json"
category_path = "../../data/backup/category_tree.json"


def get_all_category_iter(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield key, value
            yield from get_all_category_iter(value)
        else:
            yield key, value


with open(reviews_path) as fp:
    reviews_dict = json.load(fp)

reviews_set = set([str(elem) for elem in reviews_dict.keys()])

with open(category_path) as fp2:
    category_dict = json.load(fp2)

ct_dist = {}

for main_c in category_dict.keys():
    target_dict = category_dict[main_c]
    category_name = target_dict["category_name"]
    category_products = set(target_dict["product_list"])
    for k, v in get_all_category_iter(target_dict):
        if k == 'product_list':
            v = [str(elem) for elem in v]
            category_products.update(v)

    ct_dist[category_name] = category_products

for k, v in ct_dist.items():
    print(k, len(reviews_set & v))
