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