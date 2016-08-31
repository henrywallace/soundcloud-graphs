import json
import os
import pickle
from collections import deque
from functools import wraps
from urllib.request import urlopen
import yaml

import networkx as nx
import requests
import soundcloud


def iter_memcache(func, path='cache.pkl'):
    '''Cache for time consuming API crawls.
    '''
    @wraps
    def wrapper(*args, **kwargs):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                it = pickle.load(f)
        else:
            it = list(func(*args, **kwargs))
            with open(path, 'wb') as f:
                pickle.dump(it, f)
        return it
    return wrapper


class Crawler(soundcloud.Client):
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.load(f)
        super().__init__(client_id=self.config['client']['id'])

    def get_all(self, method):
        '''Yield resources over all pages given a method.
        '''
        resource = self.get(method, linked_partitioning=True)
        yield from resource.collection
        while hasattr(resource, 'next_href'):
            resource = self.get(resource.next_href)
            yield from resource.collection

    def favorites_graph(self, artist, depth, from_id=True):
        '''BFS generate favorites graph.
        '''
        if from_id:
            artist = self.get('/users/{}'.format(artist)).fields()

        graph = nx.Graph()
        graph.add_node(artist['id'], {
            'name': artist['username'],
            'image': artist['avatar_url'],
        })

        queue = deque([artist])
        seen = set()

        while queue and depth > 0:
            artist = queue.popleft()

            seen.add(artist['id'])

            method = '/users/{}/favorites'.format(artist['id'])
            for track in self.get_all(method):

                u, v = artist['id'], track.user['id']
                if graph.has_edge(u, v):
                    graph.edge[u][v]['weight'] += 1
                else:
                    graph.add_edge(u, v, weight=1)

                graph.node[track.user['id']] = {
                    'name': track.user['username'],
                    'image': track.user['avatar_url'],
                }

                if track.user['id'] not in seen:
                    queue.append(track.user)

            depth -= 1

        return graph


def download_likes():
    query = '/users/giraffeapple/favorites'
    for track in get_all(query):
        if track.downloadable:
            url = track.download_url + '?client_id=' + CLIENT_ID
            fmt = track.original_format
        elif track.streamable:
            url = track.stream_url
            import pdb
            pdb.set_trace()
            fmt = 'mp3'
        else:
            site_client_id = '02gUJC0hH2ct1EGOcYXQIzRFU91c72Ea'
            url = 'http://{}/i1/tracks/{}/streams?client_id={}'.format(client.host, track.id, site_client_id)                           
            resp = requests.get(url)
            data = json.loads(resp.text)
            url = data['http_mp3_128_url']
            fmt = 'mp3'

        filename = '{}.{}'.format(track.title, fmt)

        if track.label_name:
            print(track.label_name, track.title)

        # print(filename)
        continue

        with urlopen(url) as resp, open(filename, 'wb') as f:
            shutil.copyfileobj(resp, f)


if __name__ == '__main__':
    pass
