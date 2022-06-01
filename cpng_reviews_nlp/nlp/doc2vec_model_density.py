"""
각 모델의 밀도 측정을 위한 임시 코드
cpng_nlp_viz에서 코드 일부 가져옴

Density
cpng_0abcdef_total = 0.06234299351582717
cpng_0abcdef_45 = 0.05345880853285768
cpng_0abcdef_123 = 0.021859118428214582
cpng_0abcdef_extended =
"""

import networkx as nx
import queue
import pickle
from tqdm import tqdm

model_path = "../data/model/cpng_0abcdef_123/cpng_0abcdef_123_doc2vec_model.pickle"
model_tags_order_path = "../data/model/cpng_0abcdef_123/cpng_0abcdef_123_doc2vec_model_tags_order.pickle"

class Doc2vecModel:
    def __init__(self):
        self.model_path = model_path
        self.model_tags_order_path = model_tags_order_path
        self.model, self.tags_order = self.open_model_tags_order()
        self.search_table_by_id = \
            {str(elem[0]): {"index": index, "name": elem[1]} for elem, index in
             zip(self.tags_order, range(len(self.tags_order)))}
        self.search_table_by_name = \
            {str(elem[1]): {"index": index, "id": str(elem[0])} for elem, index in
             zip(self.tags_order, range(len(self.tags_order)))}

    def open_model_tags_order(self):
        with open(self.model_path, 'rb') as fp:
            model = pickle.load(fp)

        with open(self.model_tags_order_path, 'rb') as fp:
            tags_order = pickle.load(fp)

        return model, tags_order

    def is_id_exist(self, product_id):
        if product_id in self.search_table_by_id:
            return True
        else:
            return False

    def get_name_by_product_id(self, product_id):
        if self.is_id_exist(product_id):
            product_name = self.search_table_by_id[product_id]['name']
        else:
            product_name = ""
        return product_name

    def get_products_by_keyword(self, target_input):
        return [(v['id'], k) for k, v in self.search_table_by_name.items() if target_input in k]

    def get_most_similar(self, product_id):
        if self.is_id_exist(product_id):
            index = self.search_table_by_id[product_id]['index']
            similar_product = self.model.dv.most_similar(index)

            output_list = []
            for elem in similar_product:
                p_id = self.tags_order[elem[0]][0]
                p_name = self.tags_order[elem[0]][1]
                dist = elem[1]
                output_list.append((p_id, p_name, dist))
            return output_list
        else:
            return []

    def get_new_product(self, product_id):
        pass


def build_network_structure(start_product_id):
    dv = Doc2vecModel()

    products_on_graph = {start_product_id: {
        'id': start_product_id,
        'name': dv.get_name_by_product_id(start_product_id)
    }}

    edges_set = set()

    escape_cnt = 0
    q = queue.Queue()

    q.put(start_product_id)

    while len(products_on_graph) < 300 or escape_cnt < 100:

        if q.empty():
            break

        target_id = q.get()
        similar_list = dv.get_most_similar(target_id)

        for elem in similar_list:
            p_id = str(elem[0])
            p_name = elem[1]
            # dist = elem[2]
            edges_set.add((target_id, p_id))

            if p_id not in products_on_graph:
                q.put(p_id)
                products_on_graph[p_id] = {'id': p_id, 'name': p_name}

        escape_cnt += 1


    input_list = [(k, v) for k, v in products_on_graph.items()]
    ng = nx.Graph()
    ng.add_nodes_from(input_list)
    ng.add_edges_from(edges_set)
    return ng


def open_model_tags_order():
    with open(model_path, 'rb') as fp:
        model = pickle.load(fp)

    with open(model_tags_order_path, 'rb') as fp:
        tags_order = pickle.load(fp)

    return model, tags_order

model, tags_order = open_model_tags_order()
sum_degree = 0
for i in tqdm(range(10000), total=10000):
    network = build_network_structure(str(tags_order[i][0]))
    sum_degree += nx.density(network)
print(sum_degree/10000)

