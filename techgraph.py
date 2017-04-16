import numpy as np
import networkx as nx

import os
import sys
import json
import tempfile
import itertools
import subprocess
import collections

if sys.version_info.major >= 3:
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest

class TechGraph(nx.DiGraph):
    '''
    Directed tech graph
    '''
    def nearby_edges(self, source, count=100):
        return nearby_bfs(self, source, count)

    def nearby_subgraph(self, source, count=100):
        return self.subgraph(self.nearby_edges(source).flatten())

    def description(self, node):
        return node_sentence(self, node)

    def to_svg(self):
        return graph_to_svg(self)

    def to_json(self):
        return graph_to_json(self)
        
    def show(self):
        import matplotlib.pyplot as plt
        nx.draw(self, with_labels=True)
        plt.show()
    
def nearby_bfs(G, source, count=100):
    '''
    Find edges bidirectionally from node 'source' on nx.DiGraph G. 
    max_edges: maximum number of edges to return.
    '''
    bfs_iter      = nx.bfs_edges(G, source, reverse=False)
    bfs_iter_back = nx.bfs_edges(G, source, reverse=True)
    edges = collections.deque()
    for a,b in zip_longest(bfs_iter, bfs_iter_back):
        if a is not None: edges.append(a)
        if b is not None: edges.append(b[::-1])
        if len(edges) >= count: break
            
    edges = np.array(edges)[:count]
    
    return edges
    
def json_to_graph(data):
    '''
    Load a properly formatted JSON blob into a TechGraph object
    
    Parameters
    ------------
    blob: str, or bytes
    
    Returns
    ------------
    graph: TechGraph object
    '''
    
    blob = json.loads(data)
    
    graph = TechGraph()
    graph.add_nodes_from(blob['nodes'])
    graph.add_edges_from(blob['edges'])

    return graph

def graph_to_json(graph):
    '''
    Convert a TechGraph to a JSON string. 
    
    We write our own exporter to preserve both node and edge attributes.
    
    Parameters
    -----------
    graph: TechGraph object
    
    Returns
    -----------
    as_json: str, graph formatted as JSON blob
    '''
    nodes = [[i,k] for i,k in graph.node.items()]
    blob = {'nodes' : nodes,
            'edges' : graph.edges()}

    as_json = json.dumps(blob)
    
    return as_json
    
def node_sentence(graph, node):
    '''
    Given a node and a valid techgraph, generate a sentence that describes how the
    node is generated.

    EG:
    In:  node_sentence('cooking', graph)
    Out: 'in order to produce 'cooking', all of the following are required: edible matter, heat source 

    In:  node_sentence('edible matter', graph)
    Out: 'in order to produce 'edible matter', any of the following are required: 'meat', 'edible plant matter'

    Parameters
    -----------
    graph: TechGraph object
    '''
    
    logic = ['all', 'any'][int(graph.node[node]['any'])]
    predecessors = ', '.join(graph.predecessors(node))

    sentence  = 'To create {node}, {logic} ' 
    sentence += 'of the following are required: {predecessors}'
    
    sentence = sentence.format(node  = node,
                               logic = logic,
                               predecessors = predecessors)
    return sentence

def graph_to_svg(graph):
    '''
    Convert a graph to an SVG file.
    
    Parameters
    -----------
    graph: Graph object
    
    Returns
    -----------
    svg: str, SVG format image
    '''
    dot_file = tempfile.NamedTemporaryFile()
    nx.drawing.nx_agraph.write_dot(graph, dot_file.name)
    svg = subprocess.check_output(['dot', dot_file.name, '-Tsvg'])
    dot_file.close()
    return svg
    
def format_name(name):
    '''
    Format a node name into title case and remove extra whitespace
    
    Parameters
    -----------
    name: str, name to be formatted
    
    Returns
    -----------
    cleaned: str, name but cleaned
    '''
    name = str(name)
    cleaned = ' '.join(name.split()).title()
    return cleaned
    
def load_techgraph(file_obj):
    '''
    Load a file into a TechGraph object
    
    Parameters
    -----------
    file_obj: file object 
              str of file name
              str of json- formatted data
              
    Returns
    ------------
    graph: TechGraph object
    '''
    if hasattr(file_obj, 'read'):
        return json_to_graph(file_obj.read())
    elif isinstance(file_obj, str):
        with open(file_obj, 'r') as f:
            return json_to_graph(f.read())
    else:
        raise ValueError('file_obj passed was not a file!')
        
if __name__ == '__main__':
    # load an example file for funsies
    g = load_techgraph('data/pancake.json')

    