import json
import networkx as nx
from networkx.readwrite import json_graph
import flask
import bottle
import webbrowser
import os
from crawler import Crawler
from itertools import islice
from collections import Counter
from pprint import pprint


crawler = Crawler()
graph = crawler.favorites_graph('clakclakboomclak', 3)

d = json_graph.node_link_data(graph)
json.dump(d, open('display/graph.json','w'))

app = flask.Flask(__name__, static_folder="display")

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)
print('http://localhost:8000/index.html')

app.run(port=8000)
