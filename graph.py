import json
from networkx.readwrite import json_graph
import flask
from crawler import Crawler


crawler = Crawler('config.yaml')
graph = crawler.favorites_graph('clakclakboomclak', 2)

# keep only those nodes with at least degree 2
graph = graph.subgraph([n for n, d in graph.degree().items()
                        if d > 1])

d = json_graph.node_link_data(graph)
json.dump(d, open('display/graph.json', 'w'))

app = flask.Flask(__name__, static_folder="display")


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)
print('http://localhost:8000/index.html')

app.run(port=8000)
