from os import listdir
from os.path import isfile, join
from pprint import pprint
import json
reviews_path = "../data/reviews/ramyeon/ramyeon"
output_sum_dict = {}
for f in listdir(reviews_path):
    with open(join(reviews_path,f)) as fp:
        tmp = json.load(fp)
        output_sum_dict[f[:-5]] = tmp

pprint(output_sum_dict)

# ------------------------------------- #

from os import listdir
from os.path import isfile, join
import json
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

from os import listdir
from os.path import isfile, join
import os
from pprint import pprint
import json

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