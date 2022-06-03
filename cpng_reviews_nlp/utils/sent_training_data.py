import json
from tqdm import tqdm
import pickle
from sklearn.model_selection import train_test_split
import csv
from cpng_reviews_nlp.nlp.simple_preprocessor import SimplePreprocessor


def new_sent_phrase_list():
    with open('../data/reviews/0abcdef.json') as fp:
        products = json.load(fp)

    sp = SimplePreprocessor()

    sent_phrase_list = []

    for elem in tqdm(products.values(), total=len(products)):
        reviews = elem['reviews']

        positive_rv = ''
        negative_rv = ''

        for review in reviews:
            if review['rating'] in ['1', '2', '3']:
                negative_rv += review['data'] + '\n'
            else:
                positive_rv += review['data'] + '\n'

        min_len = min(len(positive_rv), len(negative_rv))
        if min_len < 2000:
            continue

        positive_min_rv_list = positive_rv[:min_len].split('\n')
        negative_min_rv_list = negative_rv[:min_len].split('\n')

        for pos in positive_min_rv_list:
            for p in sp.preprocessing_tuple(pos):
                sent_phrase_list.append(['POS', ' '.join(p)])
        for neg in negative_min_rv_list:
            for n in sp.preprocessing_tuple(neg):
                sent_phrase_list.append(['NEG', ' '.join(n)])

    with open('sent_phrase_list.pickle', 'wb') as fp:
        pickle.dump(sent_phrase_list, fp)

def write_train_test_csv():
    with open('sent_phrase_list.pickle', 'rb') as fp:
        sent_phrase_list = pickle.load(fp)

    x_train, x_test = train_test_split(sent_phrase_list, test_size=0.2)

    print(len(x_train))
    print(len(x_test))

    with open("phrase_sent_train.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(x_train)
    with open("phrase_sent_test.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(x_test)









