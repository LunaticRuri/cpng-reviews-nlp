"""
쿠팡 리뷰 데이터를 이용한 간단한 FastText 모델
"""
from cpng_reviews_nlp.nlp.preprocessor import Preprocessor
from gensim.test.utils import datapath
import json
from tqdm import tqdm
import re
from gensim.models import FastText
import pickle
import multiprocessing


def preprocessing(raw_text):
    output = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s]', "", raw_text)
    return output


def make_corpus_file():
    r_path = "../data/reviews/0abcdef.json"

    with open(r_path, 'r') as f:
        product_reviews = json.load(f)

    reviews_list = []

    for elem in tqdm(product_reviews.values()):
        for pair in elem["reviews"]:
            data = pair["data"]
            if not data:
                continue

            r_split = data.split("\n")

            reviews_list.extend(r_split)

    # pp = Preprocessor(Preprocessor.MORPHS)
    processed_data = []
    for sentence in tqdm(reviews_list):
        processed_data.append(preprocessing(sentence))

    with open('../data/model/ft/reviews_corpus.txt', 'w+') as f:
        f.write('\n'.join(processed_data))


def new_ft_model():
    # absolute path
    corpus_file = datapath('/Users/yggnamu/Downloads/nlp_project/cpng-reviews-nlp/data/model/ft/reviews_corpus.txt')

    model = FastText(
        vector_size=300,
        window=5,
        min_count=5,
        workers=multiprocessing.cpu_count(),
        sg=1
    )

    model.build_vocab(corpus_file=corpus_file)

    total_words = model.corpus_total_words
    print("total_words: ", total_words)

    model.train(corpus_iterable=corpus_file, total_words=total_words, epochs=10)

    with open('../data/model/ft/cpng_reviews_ft.pickle', 'wb') as fp:
        pickle.dump(model, fp)


def load_model():
    with open('../data/model/ft/cpng_reviews_ft.pickle', 'rb') as fp:
        model = pickle.load(fp)
    return model


def run_model(model):
    print(model.wv.vectors.shape)

    print(model.wv.similarity('노트북', '사과'))


# make_corpus_file()
# new_ft_model()

model = load_model()
run_model(model)
