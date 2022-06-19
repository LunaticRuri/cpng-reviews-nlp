"""
쿠팡 리뷰 데이터를 간단한 word2vec 모델
"""

from konlpy.tag import Mecab
import json
from tqdm import tqdm
import re
from gensim.models import Word2Vec
import pickle


stop_pos = ['JX', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'EF', 'IC',
            'JC', 'SY', 'EP', 'MM', 'NNBC', 'NP', 'EC', 'VCP', 'NMB', 'MAG']


def preprocessing(raw_text):
    """
    초성 지우고 한글과 공백 하나만을 남김
    :param raw_text: 리뷰 데이터 그대로
    :return:
    """
    output = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s]', "", raw_text)
    return output


def pos_remover(token_pos_list):
    return []

def new_model():
    """
    새로운 Word2Vec 모델 학습
    """
    path = "../data/reviews/0abcdef.json"

    with open(path, 'r') as f:
        product_reviews = json.load(f)

    reviews_list = []

    for elem in tqdm(product_reviews.values()):
        for pair in elem["reviews"]:
            data = pair["data"]
            if not data:
                continue

            # 한 rating에 분량이 4000자 이상이면 4000자로 자르기
            if len(data) >= 4000:
                data = data[:4000]

            r_split = [preprocessing(review) for review in data.split("\n")]

            reviews_list.extend(r_split)


    # 형태소 분석기 mecab를 사용한 토큰화 작업 (다소 시간 소요)
    mc = Mecab()

    tokenized_data = []
    for sentence in tqdm(reviews_list):
        tokenized_sentence = mc.pos(sentence)  # 토큰화
        stopwords_removed_sentence = [pair[0] for pair in tokenized_sentence if not pair[1] in stop_pos]  # 불용어 제거
        tokenized_data.append(stopwords_removed_sentence)

    model = Word2Vec(sentences=tokenized_data, vector_size=300, window=5, min_count=5, workers=5, sg=0)

    with open('../data/model/cpng_0abc_filtered_word2vec.pickle', 'wb') as fp:
        pickle.dump(model, fp)


def load_model():
    """
    pickle로 저장한 gensim의 Word2vec 모델을 반환
    :return: Word2Vec model
    """
    with open('../data/model/cpng_0abc_filtered_word2vec.pickle', 'rb') as fp:
        model = pickle.load(fp)
    return model


def run_model(model):
    """
    model 출력 확인
    """
    # 생각보다 그렇게 잘 나오지는 않는다.
    print(model.wv.vectors.shape)
    print(model.wv.most_similar(positive=["휴대폰", "컴퓨터"]))
    print(model.wv.most_similar(positive=["신라면"], negative=["삼양라면"]))
    print(model.wv.most_similar(positive=["컴퓨터", "시계"]))
    print(model.wv.most_similar(positive=["차", "그릇"]))
    print(model.wv.most_similar(positive=["스마트폰"], negative=["안드로이드"]))


#new_model()
model = load_model()
run_model(model)