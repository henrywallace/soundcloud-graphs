import json
import os
import pickle
from collections import Counter, deque
from functools import lru_cache, partial, wraps
from urllib.request import urlopen
from itertools import islice

import networkx as nx
import requests
import soundcloud


def iter_memcache(func):
    path = 'cache.pkl'
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
    CLIENT_ID = '44e0c1f64e3a46e29c64a920932a8f09'
    CLIENT_SECRET = 'fe853d1167fdb2ad573ad57f2c41e115'

    def __init__(self):
        super().__init__(client_id=self.CLIENT_ID)

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
    
# artist = 'clakclakboomclak'
# counts = Counter()
# for track in likes(artist):
#     # user_id = track.user_id
#     counts[track.user['username']] += 1




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
        # if '-' not in filename and not filename.startswith('Slime'):
            # import pdb
            # pdb.set_trace()
        if track.label_name:
            print(track.label_name, track.title)
            
        # print(filename)
        continue
    
        with urlopen(url) as resp, open(filename, 'wb') as f:
            shutil.copyfileobj(resp, f)
        
if __name__ == '__main__':
    # download_likes()
    graph = Crawler().favorites_graph('clakclakboomclak', 1)
    import pdb
    pdb.set_trace()
    pass
