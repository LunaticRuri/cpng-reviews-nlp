import json
import re
import random
import csv
from tqdm import tqdm


def preprocessor(raw_text):
    r_hangul = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s\d.]', "", raw_text)
    return r_hangul


with open('../data/backup/0abcdef.json') as fp:
    reviews_json = json.load(fp)

bad_reviews = []
good_reviews = []

for elem in tqdm(reviews_json.values(), total=len(reviews_json)):
    reviews = elem['reviews']
    for rv in reviews:
        if 1 <= int(rv['rating']) <= 3:
            bad_reviews.extend([preprocessor(text) for text in rv['data'].split('\n')])
        else:
            good_reviews.extend([preprocessor(text) for text in rv['data'].split('\n')])


random.shuffle(bad_reviews)
random.shuffle(good_reviews)

print(f"bad: {len(bad_reviews)}, good: {len(good_reviews)}")
print(f"bad: {bad_reviews[:10]}")
print(f"good: {good_reviews[:10]}")

train_set = [(bad, 0) for bad in bad_reviews[:1000000]] + \
            [(good, 1) for good in good_reviews[:1000000]]

test_set = [(bad, 0) for bad in bad_reviews[-100000:]] + \
            [(good, 1) for good in good_reviews[-100000:]]

random.shuffle(train_set)
random.shuffle(test_set)

# write TSV files
with open('../data/sent_data/sent_train_mini.tsv', 'w', encoding='utf-8', newline='') as f1:
    tw1 = csv.writer(f1, delimiter='\t')
    tw1.writerow(('document', 'label'))
    for elem in train_set:
        tw1.writerow(elem)

with open('../data/sent_data/sent_test_mini.tsv', 'w', encoding='utf-8', newline='') as f2:
    tw2 = csv.writer(f2, delimiter='\t')
    tw2.writerow(('document', 'label'))
    for elem in test_set:
        tw2.writerow(elem)


