from konlpy.tag import Mecab
from tqdm import tqdm
import re
import json
import pickle
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedLineDocument

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


def json_to_list(json_elem):
    sum_of_reviews: str = ""

    for pair in json_elem["reviews"]:
        data = pair["data"]
        if not data:
            continue
        pp = preprocessing(data)
        if len(pp) >= 8000:
            pp = pp[:8000]
        sum_of_reviews += pp

    if len(sum_of_reviews) >= 10000:
        output_list = [json_elem['product_id'], json_elem['product_name'], sum_of_reviews]
    else:
        output_list = []

    return output_list


def reviews_tokenizer(text):
    """
    output_text = stopword(
        mecab.morphs(spell_checker.check(input_row['reviews']).checked)
        )
    """
    output_text = stopword(mecab.morphs(text))

    return output_text


def new_model():
    reviews_path = "../data/reviews/0abc.json"

    with open(reviews_path, 'r') as f:
        product_reviews = json.load(f)

    # id, name, reviews

    th_list = []

    for elem in tqdm(product_reviews.values(), total=len(product_reviews)):
        result = json_to_list(elem)
        if result:
            th_list.append(result)

    print("th_list len", len(th_list))

    tagged_corpus_list = []

    tags_order = []

    for elem in tqdm(th_list, total=len(th_list)):
        tag_name_pair = (elem[0], elem[1])
        text = ' '.join(reviews_tokenizer(elem[2]))

        tags_order.append(tag_name_pair)
        tagged_corpus_list.append(text)

    print(tags_order)

    with open("cpng_tagged_line_document.space", 'w+') as fp:
        for item in tagged_corpus_list:
            fp.write(item + '\n')

    print("***********************************")

    tagged_docs = TaggedLineDocument("cpng_tagged_line_document.space")

    model = doc2vec.Doc2Vec(
        vector_size=300,
        alpha=0.025,
        min_alpha=0.025,
        workers=8,
        window=5,
        min_count=5,
    )

    print("model.build_vocab")

    model.build_vocab(tagged_docs)

    print("model.train()")

    model.train(tagged_docs, total_examples=model.corpus_count, epochs=20)

    print("Saving data...")

    with open("../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model.pickle", 'wb') as fp:
        pickle.dump(model, fp)
    with open("../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model_tags_order.pickle", 'wb') as fp:
        pickle.dump(tags_order, fp)


def open_model_tags_order():
    with open("../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model.pickle", 'rb') as fp:
        model = pickle.load(fp)

    with open("../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model_tags_order.pickle", 'rb') as fp:
        tags_order = pickle.load(fp)

    return model, tags_order


def run(model, tags_order):
    index = 100
    similar_product = model.docvecs.most_similar(index)
    print(tags_order[index])
    for elem in similar_product:
        print(tags_order[elem[0]], elem[1])


model, tags_order = open_model_tags_order()
run(model, tags_order)
