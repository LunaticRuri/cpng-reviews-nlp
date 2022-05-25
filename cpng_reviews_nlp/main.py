from konlpy.tag import Mecab
import json
from tqdm import tqdm
import re
from gensim.models import Word2Vec


def preprocessing(raw_text):
    output = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s+]', "", raw_text)
    return output


ll = ['0', 'a', 'b', 'c']
path = "../data/reviews/0abc.json"

with open(path, 'r') as f:
    product_reviews = json.load(f)

reviews_list = []

for elem in tqdm(product_reviews.values()):
    for pair in elem["reviews"]:
        data = pair["data"]
        if not data:
            continue

        r_split = [preprocessing(review) for review in data.split("\n")]

        reviews_list.extend(r_split)

# 불용어 정의
stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']

# 형태소 분석기 mecab를 사용한 토큰화 작업 (다소 시간 소요)
mecab = Mecab()

tokenized_data = []
for sentence in tqdm(reviews_list):
    tokenized_sentence = mecab.morphs(sentence)  # 토큰화
    stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stopwords]  # 불용어 제거
    tokenized_data.append(stopwords_removed_sentence)

model = Word2Vec(sentences=tokenized_data, vector_size=300, window=5, min_count=5, workers=4, sg=0)

print(model.wv.vectors.shape)
print(model.wv.most_similar(positive=["휴대폰", "컴퓨터"]))
print(model.wv.most_similar(positive=["신라면"], negative=["삼양라면"]))
print(model.wv.most_similar(positive=["컴퓨터", "시계"]))
print(model.wv.most_similar(positive=["차", "그릇"]))
print(model.wv.most_similar(positive=["스마트폰"], negative=["안드로이드"]))

model.wv.save_word2vec_format('cpng0abc_word2vec')
