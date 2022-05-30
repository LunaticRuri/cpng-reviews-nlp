import networkx as nx
import random
from bokeh.plotting import figure, curdoc
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool, TapTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh.events import Tap
from bokeh.models import (ColumnDataSource, DataTable, LabelSet,
                          TableColumn, Panel, Tabs, Paragraph)
from bokeh.layouts import column, row
from bokeh.models import Button, CustomJS, Div, TextInput, Select
import pickle
from bokeh.client import push_session, pull_session
from gensim.models import doc2vec
import queue
from pprint import pprint


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


class Doc2vecModel:
    def __init__(self):
        self.model_path = "../../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model.pickle"
        self.model_tags_order_path = "../../data/model/cpng_0abcde/cpng_0abcde_doc2vec_model_tags_order.pickle"
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


class EventHandler:
    def __init__(self):
        pass

    @staticmethod
    def network_search_btn_handler():
        target_input = network_id_input.value_input
        if d2v.is_id_exist(target_input):

            target_id = target_input
            target_name = d2v.get_name_by_product_id(target_id)


            network_div.text = \
                f"""<b>Product ID: </b> {target_id} <br><b>Name: </b> {target_name}<br>"""\
                f"""<b>Link: </b><a href="https://www.coupang.com/vp/products/{target_id}">쿠팡 상품 페이지</a>"""

            new_plot = Plot(title="CPNG_NLP_VS", width=1400, height=650, x_range=Range1d(-1.1, 1.1),
                        y_range=Range1d(-1.1, 1.1))

            new_G = build_network_structure(target_id)

            # toolbar
            new_plot.add_tools(node_hover_tool, TapTool(), BoxZoomTool(), ResetTool())

            # graph renderer networkx
            new_graph_renderer = from_networkx(new_G, nx.spring_layout, scale=1, center=(0, 0))

            new_graph_renderer.node_renderer.glyph = Circle(size=10, fill_color=Spectral4[0])
            new_graph_renderer.edge_renderer.glyph = MultiLine(
                line_color="black",
                line_alpha=0.8,
                line_width=1
            )

            new_plot.renderers.append(new_graph_renderer)

            network_layout.children[2] = new_plot
        else:
            matching = d2v.get_products_by_keyword(target_input)
            if not matching:
                network_div.text = "데이터에 없는 상품이거나 잘못된 번호입니다. (리소스 부족으로 상품 데이터 받아오기 안됨)"
            else:
                target_product = random.choice(matching)
                target_id = target_product[0]
                target_name = target_product[1]

                network_div.text = \
                    f"""<b>Product ID: </b> {target_id} <br><b>Name: </b> {target_name}<br>""" \
                    f"""<b>Link: </b><a href="https://www.coupang.com/vp/products/{target_id}">쿠팡 상품 페이지</a>"""

                new_plot = Plot(title="CPNG_NLP_VS", width=1400, height=650, x_range=Range1d(-1.1, 1.1),
                                y_range=Range1d(-1.1, 1.1))

                new_G = build_network_structure(target_id)

                # toolbar
                new_plot.add_tools(node_hover_tool, TapTool(), BoxZoomTool(), ResetTool())

                # graph renderer networkx
                new_graph_renderer = from_networkx(new_G, nx.spring_layout, scale=1, center=(0, 0))

                new_graph_renderer.node_renderer.glyph = Circle(size=10, fill_color=Spectral4[0])
                new_graph_renderer.edge_renderer.glyph = MultiLine(
                    line_color="black",
                    line_alpha=0.8,
                    line_width=1
                )

                new_plot.renderers.append(new_graph_renderer)

                network_layout.children[2] = new_plot

    @staticmethod
    def search_btn_handler():
        print()

# Prepare Data
start_id = "2437845"
G = build_network_structure(start_id)
d2v = Doc2vecModel()
similar_top_list = d2v.get_most_similar(start_id)

# recommendation system
id_input = TextInput(value="이곳에 키워드 또는 Product ID 입력 (Ex: 라면 or 2437845)", width=600)
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

# network cpng_nlp_viz

plot = Plot(title="CPNG_NLP_VS", width=1400, height=650, x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))

explanation_p = Paragraph(
    text="리뷰를 기준으로 유사 상품 300개를 네트워크 형식으로 도출함",
    width=plot.width,
    height=10
)

network_id_input = TextInput(value="이곳에 키워드 또는 Product ID 입력 (Ex: 라면 or 2437845)", width=600)

network_search_btn = Button(label="Search", button_type="success")
network_search_btn.on_click(EventHandler.network_search_btn_handler)

network_div = Div(width=400, height=50, height_policy="fixed")

network_layout = column(
    explanation_p,
    row(network_id_input, network_search_btn, network_div),
    plot,
)

network_tab = Panel(child=network_layout, title="Network")

node_hover_tool = HoverTool(
    tooltips=[
        ("id", "@id"),
        ("name", "@name"),
    ])

# toolbar
plot.add_tools(node_hover_tool, TapTool(), BoxZoomTool(), ResetTool())

# graph renderer networkx
graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size=10, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(
    line_color="black",
    line_alpha=0.8,
    line_width=1
)

plot.renderers.append(graph_renderer)

curdoc().add_root(Tabs(tabs=[search_tab, network_tab]))
session = push_session(curdoc())
session.show()
