from konlpy.tag import Mecab
import pandas as pd
from gensim.models.doc2vec import TaggedDocument
from gensim.models import doc2vec
from tqdm import tqdm
import re
import json
from hanspell import spell_checker

mecab = Mecab()


def preprocessing(raw_text):
    r_hangul = re.sub(r'[^ㄱ-ㅣ가-힣ㅣ\s+]', "", raw_text)
    return r_hangul


def stopword(word_tokenize):
    # TODO: stopwords는 나중에 따로 빼도 될 듯
    stopwords = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']
    result = []

    for w in word_tokenize:
        if w not in stopwords:
            result.append(w)

    return result


reviews_path = "../../data/reviews/0abc.json"

with open(reviews_path, 'r') as f:
    product_reviews = json.load(f)

# id, name, reviews
product_df = pd.DataFrame(columns=['id', 'name', 'reviews'])
product_df.set_index('id')

for elem in tqdm(product_reviews.values()):

    sum_of_reviews: str = ""

    for pair in elem["reviews"]:
        data = pair["data"]
        if not data:
            continue

        sum_of_reviews += preprocessing(data)

    product_df.loc[product_df.shape[0]] = [elem['product_id'], elem['product_name'], sum_of_reviews]

tagged_corpus_list = []

for index, row in tqdm(product_df.iterrows(), total=len(product_df)):
    text = stopword(mecab.morphs(spell_checker.check(row['reviews'])))
    tag = row['id']

    tagged_corpus_list.append(TaggedDocument(tags=[tag], words=text))

model = doc2vec.Doc2Vec(
    vector_size=300,
    alpha=0.025,
    min_alpha=0.025,
    workers=8,
    window=8
)

model.build_vocab(tagged_corpus_list)
print(f"Tag Size: {len(model.docvecs.doctags.keys())}", end=' / ')

model.train(tagged_corpus_list, total_examples=model.corpus_count, epochs=50)

model.save('doc2vec_0abc')

similar_product = model.docvecs.most_similar('1067207282')

print(similar_product)

similar_product = model.docvecs.most_similar('6455913779')

print(similar_product)