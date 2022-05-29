import networkx as nx
from datetime import date
from random import randint
import re
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh import events
from bokeh.models import (ColumnDataSource, DataTable, DateFormatter,
                          TableColumn, Panel, Tabs, Paragraph)
from bokeh.layouts import column, row
from bokeh.models import Button, CustomJS, Div, TextInput, Select
import pickle
from gensim.models import doc2vec
import queue
from pprint import pprint


class Doc2vecModel:
    def __init__(self):
        self.model_path = "../../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model.pickle"
        self.model_tags_order_path = "../../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model_tags_order.pickle"
        self.model, self.tags_order = self.open_model_tags_order()
        self.search_table_by_id = \
            {str(elem[0]): {"index": index, "name": elem[1]} for elem, index in
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

    def get_most_similar(self, product_id):
        if self.is_id_exist(product_id):
            index = self.search_table_by_id[product_id]['index']
            similar_product = self.model.docvecs.most_similar(index)
            print(self.tags_order[index])

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
        if not q:
            raise SystemExit("build_network_structure err: q is empty")
        target_id = q.get()
        print(target_id)
        similar_list = dv.get_most_similar(target_id)

        for elem in similar_list:
            print("inner:", elem)
            p_id = elem[0]
            p_name = elem[1]
            # dist = elem[2]
            edges_set.add((target_id, p_id))
            if p_id not in products_on_graph:
                q.put(p_id)
                products_on_graph[p_id] = {'id': p_id, 'name': p_name}

        escape_cnt += 1

    ng = nx.Graph()
    ng.add_nodes_from(products_on_graph)
    ng.add_edges_from(edges_set)
    return ng


# Prepare Data
test_id = "2437845"
G = build_network_structure(test_id)
d2v = Doc2vecModel()
similar_top_list = d2v.get_most_similar(test_id)

# recommendation system
id_input = TextInput(value="2437845")
search_btn = Button(label="Search", button_type="success")

data = {
    "id": [elem[0] for elem in similar_top_list],
    "name": [elem[1] for elem in similar_top_list],
    "dist": [elem[2] for elem in similar_top_list],
}

source = ColumnDataSource(data)

columns = [
    TableColumn(field="id", title="Product ID"),
    TableColumn(field="name", title="Name"),
    TableColumn(field="dist", title="Distance"),
]

data_table = DataTable(source=source, columns=columns, width=600, height=300)

div = Div(width=600, height=400, height_policy="fixed")

search_layout = column(row(id_input, search_btn), div, data_table)
search_tab = Panel(child=search_layout, title="Search")

# network visualization
plot = Plot(width=1400, height=650,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "CPNG_NLP_VS"

explanation_p = Paragraph(
    text="리뷰를 기준으로 유사 상품 300개를 네트워크 형식으로 도출함",
    width=plot.width,
    height=10
)

network_id_input = TextInput(value="2437845")
network_search_btn = Button(label="Search", button_type="success")

network_layout = column(explanation_p, row(network_id_input, network_search_btn), plot)
network_tab = Panel(child=network_layout, title="Network")

node_hover_tool = HoverTool(
    tooltips=[
        ("id", "@id"),
        ("name", "@name"),
    ])

# toolbar
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

# graph renderer networkx
graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size=10, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(
    line_color="black",
    line_alpha=0.8,
    line_width=1
)

plot.renderers.append(graph_renderer)

# output
output_file("recommend_network_visualization.html")

show(Tabs(tabs=[search_tab, network_tab]))
