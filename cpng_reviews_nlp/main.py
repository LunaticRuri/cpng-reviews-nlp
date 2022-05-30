from os import listdir
from os.path import join
import json
reviews_path = "../data/dividing/tmp_reviews/"
merge_dict = "../data/reviews/0abcde.json"

with open(merge_dict) as fp:
    output_sum_dict = json.load(fp)

for f in listdir(reviews_path):
    with open(join(reviews_path, f)) as fp:
        tmp = json.load(fp)
        output_sum_dict[f[:-5]] = tmp

with open("../data/reviews/0abcdef.json", 'w+') as fp:
    json.dump(output_sum_dict, fp, ensure_ascii=False)