"""
리뷰 JSON 파일 관련 code snippet
"""
import os
from os import listdir
from os.path import join
from pprint import pprint
import json

# ------------------------------------- #

# 각 상품이 각기 다른 파일로 저장이 되었을 때 dict로 합치기
reviews_path = "../data/reviews/ramyeon/ramyeon"
output_sum_dict = {}
for f in listdir(reviews_path):
    with open(join(reviews_path,f)) as fp:
        tmp = json.load(fp)
        output_sum_dict[f[:-5]] = tmp

pprint(output_sum_dict)

# ------------------------------------- #

# dividing 작업이 마무리 되었을 경우에 받아온 것 기존 자료랑 합치기
reviews_path = "../data/dividing/tmp_reviews/"
merge_dict = "../data/reviews/0abc.json"

with open(merge_dict) as fp:
    output_sum_dict = json.load(fp)

for f in listdir(reviews_path):
    with open(join(reviews_path, f)) as fp:
        tmp = json.load(fp)
        output_sum_dict[f[:-5]] = tmp

with open("../data/reviews/0abcp.json", 'w+') as fp:
    json.dump(output_sum_dict, fp, ensure_ascii=False)

# ------------------------------------- #

# 상품 파일 중 리뷰가 하나도 포함되어 있지 않은 파일 지우기
reviews_path = "../data/dividing/tmp_reviews/"
output_sum_dict = {}
for f in listdir(reviews_path):
    with open(join(reviews_path, f)) as fp:
        tmp = json.load(fp)
        rv_cnt = 0
        for elem in tmp["reviews"]:
            if not elem['data']:
                rv_cnt += 1

    if rv_cnt == 5:
        print(f"rm {f}")
        os.remove(join(reviews_path, f))