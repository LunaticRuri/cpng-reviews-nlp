import networkx as nx
from datetime import date
from random import randint
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from bokeh import events
from bokeh.models import ColumnDataSource, DataTable, DateFormatter, TableColumn
from bokeh.layouts import column, row
from bokeh.models import Button, CustomJS, Div, TextInput


class Doc2vecModel:
    pass

class EventHandler:
    pass

def add_node(product_code):
    pass




# Prepare Data
G = nx.Graph()

G.add_nodes_from([
    (1, {"product_name": "red"})
])
G.add_node(2)
G.add_node(3)

# Show with Bokeh
plot = Plot(width=800, height=650,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "CPNG_NLP_VS"
plot.toolbar.logo = None
plot.toolbar_location = None

reset_btn = Button(label="Reset", button_type="success")

text_input = TextInput(value="default")
search_btn = Button(label="Search", button_type="success")

data = dict(
        dates=[date(2014, 3, i+1) for i in range(10)],
        downloads=[randint(0, 100) for i in range(10)],
    )
source = ColumnDataSource(data)
columns = [
        TableColumn(field="dates", title="Date", formatter=DateFormatter()),
        TableColumn(field="downloads", title="Downloads"),
    ]
data_table = DataTable(source=source, columns=columns, width=600, height=300)

div = Div(width=600, height=300, height_policy="fixed")

layout = column(row(plot, column(row(text_input, search_btn), div, data_table)), reset_btn)

node_hover_tool = HoverTool(tooltips=[("id", "@index"), ("name", "@product_name")])
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)
plot.renderers.append(graph_renderer)

output_file("recommend_network_visualization.html")
show(layout)
