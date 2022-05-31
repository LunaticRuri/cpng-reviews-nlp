from bokeh.layouts import column, row
from bokeh.models import (BoxZoomTool, HoverTool, TapTool, ResetTool,
                          MultiLine, Circle, Plot, Range1d, ColumnDataSource,
                          DataTable, Button, Div, TextInput,
                          TableColumn, Panel, Tabs, Paragraph)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

from bokeh.plotting import curdoc
from bokeh.client import push_session

from bs4 import BeautifulSoup
import networkx as nx
import requests
import urllib3
import pickle
import random
import queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


class Doc2vecModel:
    def __init__(self):
        self.model_path = "./model/cpng_0abcdef_doc2vec_model.pickle"
        self.model_tags_order_path = "./model/cpng_0abcdef_doc2vec_model_tags_order.pickle"
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
    def update_network_product_desc(target_id, target_name):
        center_style = \
            """
            <style>
            p {text-align: center;}
            div {text-align: center;}
            table {text-align: center;}
            </style>
            """

        network_div.text = \
            f"""
            {center_style}
            <table border="1">
            <tr>
            <!-- First row -->
            <td><b>Product ID</b></td><td>{target_id}</td>
            </tr>
            <tr>
            <!-- Second row -->
            <td><b>Name</b></td><td>{target_name}</td>
            </tr>
            <tr>
            <!-- Third row -->
            <td><b>Link</b></td><td><a href="https://www.coupang.com/vp/products/{target_id}">쿠팡 상품 페이지</a></td>
            </tr>
            <tr>
            </table>
            """

    @staticmethod
    def update_density_div(network):
        density_div.text = f"<b>Density: </b>{nx.density(network)}"


    @staticmethod
    def update_network_plot(target_id):
        new_plot = Plot(title="CPNG_NLP_VS", width=1400, height=650, x_range=Range1d(-1.1, 1.1),
                        y_range=Range1d(-1.1, 1.1))

        new_g = build_network_structure(target_id)

        # density div update
        EventHandler.update_density_div(new_g)

        # toolbar
        new_plot.add_tools(node_hover_tool, TapTool(), BoxZoomTool(), ResetTool())

        # graph renderer networkx
        new_graph_renderer = from_networkx(new_g, nx.spring_layout, scale=1, center=(0, 0))

        new_graph_renderer.node_renderer.glyph = Circle(size=10, fill_color=Spectral4[0])
        new_graph_renderer.edge_renderer.glyph = MultiLine(
            line_color="black",
            line_alpha=0.8,
            line_width=1
        )

        new_plot.renderers.append(new_graph_renderer)

        network_layout.children[2] = new_plot

    @staticmethod
    def network_search_btn_handler():
        target_input = network_id_input.value_input
        if d2v.is_id_exist(target_input):

            target_id = target_input
            target_name = d2v.get_name_by_product_id(target_id)

            EventHandler.update_network_product_desc(target_id, target_name)

            EventHandler.update_network_plot(target_id)

        else:
            matching = d2v.get_products_by_keyword(target_input)
            if not matching:
                network_div.text = "데이터에 없는 상품이거나 잘못된 번호입니다. (리소스 부족으로 상품 데이터 받아오기 안됨)"
            else:
                target_product = random.choice(matching)
                target_id = target_product[0]
                target_name = target_product[1]

                EventHandler.update_network_product_desc(target_id, target_name)

                EventHandler.update_network_plot(target_id)


    @staticmethod
    def get_product_img_url(product_id):
        HEADERS = {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                          'Version/15.4 Safari/605.1.15',
            'Cookie': 'Cookie:bm_sv=IHATECOOKIE;x-coupang-accept-language=ko_KR;',
            'Referer': f'https://www.coupang.com/',
        }
        product_url = f"https://www.coupang.com/vp/products/{product_id}"

        try:
            response = requests.get(product_url, headers=HEADERS, verify=False)
        except requests.exceptions.HTTPError:
            return False
        except requests.exceptions.ConnectionError:
            return False

        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        if not soup:
            return False

        target_soup = soup.find("img", {"class": "prod-image__detail"})

        # print(target_soup)
        if not target_soup:
            return False

        img_url = "https:" + target_soup['src']
        return img_url

    @staticmethod
    def update_product_desc(target_id, target_name):

        img_url = EventHandler.get_product_img_url(target_id)
        center_style = \
            """
            <style>
            p {text-align: center;}
            div {text-align: center;}
            img {text-align: center;}
            </style>
            """
        desc_html = \
            f"""
            {center_style}
            <table border="1">
            <tr>
            <!-- First row -->
            <td><b>Product ID</b></td><td>{target_id}</td>
            </tr>
            <tr>
            <!-- Second row -->
            <td><b>Name</b></td><td>{target_name}</td>
            </tr>
            <tr>
            <!-- Third row -->
            <td><b>Link</b></td><td><a href="https://www.coupang.com/vp/products/{target_id}">쿠팡 상품 페이지</a></td>
            </tr>
            <tr>
            <!-- Forth row -->
            <td colspan='2'><img src="{img_url}" alt="Network Error!" width="300" height="300"></td>
            </tr>
            </table>
            """
        desc_div.text = desc_html

    @staticmethod
    def update_datatable(target_id):
        global similar_top_list
        target_id = str(target_id)

        new_similar_top_list = d2v.get_most_similar(target_id)

        new_data = {
            "id": [elem[0] for elem in new_similar_top_list],
            "name": [elem[1] for elem in new_similar_top_list],
            "dist": [elem[2] for elem in new_similar_top_list],
        }
        source.data = new_data

        similar_top_list = new_similar_top_list

        data_table.update(source=source)

    @staticmethod
    def search_btn_handler():
        global similar_top_list
        target_input = id_input.value_input
        if d2v.is_id_exist(target_input):
            target_id = target_input
            target_name = d2v.get_name_by_product_id(target_id)
            id_input.value = target_id
        else:
            matching = d2v.get_products_by_keyword(target_input)
            if not matching:
                desc_div.text = "데이터에 없는 상품이거나 잘못된 번호입니다. (리소스 부족으로 상품 데이터 받아오기 안됨)"
                id_input.value = ""
                return True
            else:
                target_product = random.choice(matching)
                target_id = target_product[0]
                target_name = target_product[1]
                id_input.value = target_id

        EventHandler.update_product_desc(target_id, target_name)
        EventHandler.update_datatable(target_id)

    @staticmethod
    def row_select_handler(attr, old, new):
        global similar_top_list

        if not new:
            return True

        product_tuple = similar_top_list[new[0]]
        target_id = str(product_tuple[0])
        target_name = product_tuple[1]

        id_input.value = target_id

        EventHandler.update_product_desc(target_id, target_name)
        EventHandler.update_datatable(target_id)


# Prepare Data
start_id = "2437845"
G = build_network_structure(start_id)
d2v = Doc2vecModel()
similar_top_list = d2v.get_most_similar(start_id)

# recommendation system
id_input = TextInput(value="이곳에 키워드 또는 Product ID 입력 (Ex: 라면 or 2437845)", width=600)
search_btn = Button(label="Search", button_type="success")
search_btn.on_click(EventHandler.search_btn_handler)

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

source.selected.on_change('indices', EventHandler.row_select_handler)

data_table = DataTable(source=source, columns=columns, width=600, height=600)

desc_div = Div(width=600, height=400, height_policy="fixed")

howto_div = Div(width=600, height=20, height_policy="fixed")
howto_div.text = "<b>표의 행을 클릭해보세요!</b>"

search_layout = column(id_input, search_btn, desc_div, howto_div, data_table)
search_tab = Panel(child=search_layout, title="Search")

# network cpng_nlp_viz

plot = Plot(title="CPNG_NLP_VS", width=1200, height=600, x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))

explanation_p = Paragraph(
    text="리뷰를 기준으로 유사 상품 300개 정도를 네트워크 형식으로 도출함. "
         "버튼을 누르면 랜덤하게 네트워크 생성. 리소스 부족으로 시간이 좀 걸릴 수 있음 (다시 접속)",
    width=plot.width,
    height=10
)

network_id_input = TextInput(value="이곳에 키워드 또는 Product ID 입력 (Ex: 라면 or 2437845)", width=400)

network_search_btn = Button(label="Search", button_type="success")
network_search_btn.on_click(EventHandler.network_search_btn_handler)

network_div = Div(width=600, height=80, height_policy="fixed")

density_div = Div(width=100, height=80, height_policy="fixed")

network_layout = column(
    explanation_p,
    row(column(network_id_input, network_search_btn), network_div, density_div),
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
curdoc().title = "CPNG_NLP"
