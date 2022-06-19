"""
유사 상품 추천을 위한 Doc2Vec 모듈
"""
from preprocessor import Preprocessor
from tqdm import tqdm
import os.path
import json
import pickle
import random
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedLineDocument
import multiprocessing


class ProductDoc2vec:
    def __init__(self, reviews_path, model_path):
        self.pp = Preprocessor(mode=Preprocessor.MORPHS)
        self.reviews_path = reviews_path
        self.model_path = model_path

    def json_to_list(self, json_elem):
        sum_of_reviews: str = ""

        for pair in json_elem["reviews"]:
            data = pair["data"]
            if not data:
                continue
            rv = self.pp.only_hangul_number_space(data)
            if len(rv) >= 8000:
                rv = rv[:8000]
            sum_of_reviews += rv

        if len(sum_of_reviews) >= 10000:
            output_list = [json_elem['product_id'], json_elem['product_name'], sum_of_reviews]
        else:
            output_list = []

        return output_list

    def new_model(self):
        with open(self.reviews_path, 'r') as f:
            product_reviews = json.load(f)

        # id, name, reviews

        th_list = []

        for elem in tqdm(product_reviews.values(), total=len(product_reviews)):
            result = self.json_to_list(elem)
            if result:
                th_list.append(result)

        print("\n th_list len", len(th_list))

        tagged_corpus_list = []

        tags_order = []

        for elem in tqdm(th_list, total=len(th_list)):
            tag_name_pair = (elem[0], elem[1])
            text = ' '.join(self.pp.preprocessing(elem[2]))

            tags_order.append(tag_name_pair)
            tagged_corpus_list.append(text)

        print(tags_order)

        with open(os.path.join(self.model_path,"d2v_tagged_line_document.space"), 'w+') as fp:
            for item in tagged_corpus_list:
                fp.write(item + '\n')

        print("***********************************")
        # 메모리 부족 문제로 어쩔 수 없음
        tagged_docs = TaggedLineDocument(os.path.join(self.model_path,"d2v_tagged_line_document.space"))

        model = doc2vec.Doc2Vec(
            vector_size=300,
            alpha=0.025,
            min_alpha=0.025,
            workers=multiprocessing.cpu_count(),
            window=5,
            min_count=5,
        )

        print("model.build_vocab")

        model.build_vocab(tagged_docs)

        print("model.train()")

        model.train(tagged_docs, total_examples=model.corpus_count, epochs=20)

        print("Saving data...")

        with open(os.path.join(self.model_path, "d2v_model.pickle"), 'wb') as fp:
            pickle.dump(model, fp)
        with open(os.path.join(self.model_path, "d2v_tags_order.pickle"), 'wb') as fp:
            pickle.dump(tags_order, fp)

        return model, tags_order

    def open_model_tags_order(self):
        with open(os.path.join(self.model_path, "d2v_model.pickle"), 'rb') as fp:
            model = pickle.load(fp)

        with open(os.path.join(self.model_path, "d2v_tags_order.pickle"), 'rb') as fp:
            tags_order = pickle.load(fp)

        return model, tags_order


def test_product_doc2vec(reviews_path, model_path):

    # reviews_path = ../../data/reviews/0abcdef.json
    # model_path = ../../data/model/

    d2v = ProductDoc2vec(
        reviews_path=reviews_path,
        model_path=model_path,
    )

    d2v.new_model()
    model, tags_order = d2v.open_model_tags_order()
    index = random.randint(0, len(tags_order))

    similar_product = model.dv.most_similar(index)

    print(tags_order[index])
    print("****************************************")
    for elem in similar_product:
        print(tags_order[elem[0]], elem[1])


