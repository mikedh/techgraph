import numpy as np
import networkx as nx

import os
import sys
import json
import copy
import hashlib
import tempfile
import itertools
import subprocess
import collections

if sys.version_info.major >= 3:
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest

class TechGraph(nx.MultiDiGraph):
    '''
    Directed tech graph
    '''
    def nearby_edges(self, source, count=100):
        '''
        Find nearby edges using BFS traversal in both directions from 
        a source node on a networkx graph.
      
        Parameters
        -----------
        graph:  nx.Graph- like object
        source: hashable, name of the node in graph to start from
        count:  int, maximum number of edges to return

        Returns
        ------------
        edges: (n,2) edges in graph
        '''
        return nearby_bfs(self, source, count)

    def nearby_subgraph(self, source, count=100):
        '''
        Get a subgraph of the graph nearby a specified source node.
        
        Parameters
        -----------
        source: hashable, node name
        count:  int, maximum number of unique nodes in result
        
        Returns
        -----------
        subgraph: TechGraph, with a maximum of count nodes
        '''
        # get nearby edges with bidirectional BFS 
        nearby = self.nearby_edges(source).flatten()
        # clip nearby to specified count of unique nodes
        nearby = np.unique(nearby)[:count]
        # get the subgraph from the list of nodes
        subgraph = self.subgraph(nearby)
        return subgraph

    def description(self, node):
        '''
        Generate a sentence for humans describing the things required to create
        a specified node.
        
        Parameters
        -----------
        node: hashable, node name
        
        Returns
        -----------
        description: str, sentence describing parents of node
        '''
        description = node_sentence(self, node)
        return description
        
    def to_svg(self):
        '''
        Use pygraphviz to generate an SVG of current graph.
        
        You may want to take a smaller subgraph before running 
        this on large graphs. Require
        
        Returns
        -----------
        path: str, SVG format path string 
        '''
        return graph_to_svg(self)

    def to_json(self):
        '''
        Convert current graph to JSON string.
        
        Returns
        ----------
        as_json: str, JSON with keys ['class', 'node', 'edge']
        '''
        return graph_to_json(self)
    
    def format_nodes(self):
        '''
        Retitle every node to title case. 
        Also updates formatting in parent groups.
        '''
        mapping = {i : format_name(i) for i in self.node.keys()}
        nx.relabel_nodes(self,
                         mapping=mapping,
                         copy=False)
        for node, values in self.node.items():
            if 'parent groups' not in values:
                continue
             
            for i, g in enumerate(values['parent groups']):
                values['parent groups'][i] = format_name_node(g)

                         
    def node_info(self, node):
        info = copy.deepcopy(self.node[node])
        info['name'] = node
        info['children'] = self.successors(node)
        info['parents']  = self.predecessors(node)
        return info
        
    def node_info_update(self, info):
        '''
        Update the graph based on new node info
        '''
        for parent in info['parents']:
            self.add_edge(parent, info['name'])
        for child in info['children']:
            self.add_edge(info['name'], child)
            
        for key, value in info.items():
            if key in ['name', 'children', 'parents']:
                continue
            self.node[info['name']][key] = value

    def calculate_edge_attributes(self):
        '''
        Our logical groups are derived from the 'parent groups' node attribute.
        This is a convient place without a lot of duplication, but we would also
        often like to know which edges are optional, and which edges can be 
        substituted for other edges. 
        
        This function calculates properties for edges based on the 'parent groups'
        data stored per- node.
            
        Parameters
        -----------
        graph: TechGraph object
        '''

        calculate_edge_attributes(self)
        
    def show(self):
        '''
        Show an ugly matplotlib rendition of the current graph
        '''
        import matplotlib.pyplot as plt
        nx.draw(self, with_labels=True)
        plt.show()
    
def nearby_bfs(graph, source, count=100):
    '''
    Find nearby edges using BFS traversal in both directions from 
    a source node on a networkx graph.
  
    Parameters
    -----------
    graph:  nx.Graph- like object
    source: hashable, name of the node in graph to start from
    count:  int, maximum number of edges to return

    Returns
    ------------
    edges: (n,2) edges in graph
    '''
    bfs_iter      = nx.bfs_edges(graph, source, reverse=False)
    bfs_iter_back = nx.bfs_edges(graph, source, reverse=True)
    
    edges = collections.deque()
    for a,b in zip_longest(bfs_iter, bfs_iter_back):
        if a is not None: edges.append(a)
        if b is not None: edges.append(b[::-1])
        if len(edges) >= count: break
            
    edges = np.array(edges)[:count]
    
    return edges
    

    
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
    
    logic = ['any', 'all'][int(graph.node[node]['all_parents'])]
    predecessors = ', '.join(graph.predecessors(node))

    sentence  = 'To create {node}, {logic} ' 
    sentence += 'of the following are required: {predecessors}'
    
    sentence = sentence.format(node  = node,
                               logic = logic,
                               predecessors = predecessors)
    return sentence

def graph_to_svg(graph):
    '''
    Convert a graph to an SVG file using pygraphviz
    
    Parameters
    -----------
    graph: Graph object
    
    Returns
    -----------
    svg: str, SVG format image
    '''
    #with open('df.dot', 'w') as dot_file:
    with tempfile.NamedTemporaryFile() as dot_file:
        nx.drawing.nx_agraph.write_dot(graph, dot_file.name)
        svg = subprocess.check_output(['dot', dot_file.name, '-Tsvg'])
        
    return svg
    
def format_name_node(name, delimiter=':'):
    if is_sequence(name):
        return [format_name_node(i) for i in name]
    if name is None:
        return None
    name, key = split_key(name)
    result = delimiter.join([format_name(name), str(key)])
    return result

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
    # remove whitespace in between words as well as front and back
    cleaned = ' '.join(name.split()).title()
    return cleaned
    
def load_techgraph(file_obj):
    '''
    Load a file into a TechGraph object
    
    Parameters
    -----------
    file_obj: file object 
              str of file name
              
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
    graph.node.update(blob['node'])
    graph.edge.update(blob['edge'])
    
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
    blob = {'node' : graph.node,
            'edge' : graph.edge,
            'class' : graph.__class__.__name__}

    as_json = json.dumps(blob)
    
    return as_json
    
def is_sequence(obj):
    '''
    Figure out if an unknown object is a sequence or not.
    
    Parameters
    ------------
    obj: object which may or may not be a sequence
    
    Returns
    ------------
    sequence: bool, True if obj is a sequence and False otherwise.
    '''
    seq = (not hasattr(obj, "strip") and
           hasattr(obj, "__getitem__") or
           hasattr(obj, "__iter__"))

    seq = seq and not isinstance(obj, dict)
    seq = seq and not isinstance(obj, set)
    seq = seq and not isinstance(obj, str)
    
    # numpy sometimes returns objects that are single float64 values
    # but sure look like sequences, so we check the shape
    if hasattr(obj, 'shape'):
        seq = seq and obj.shape != ()
    return seq
  
def hash_object(obj, hasher=hashlib.sha256):
    '''
    Hash an object 
    '''
    if isinstance(obj, dict):
        obj = copy.deepcopy(obj)
        for key, value in obj.items():
            if is_sequence(value):
                obj[key] = sorted(value)
                
    as_str = json.dumps(obj, sort_keys=True, ensure_ascii=True)
    hashed = hasher(as_str.encode('utf-8'))
    as_hex = hashed.hexdigest()
    return as_hex

def split_key(name, delimiter=':', default_key=0):
    name = str(name)
    split = name.split(delimiter)
    if len(split) == 1:
        return split[0], default_key
    elif len(split) == 2:
        node, key = split
        try: 
            key = int(key)
        except ValueError:
            pass
        return node, key
    else:
        raise ValueError('\"{}\" was not formatted as \"node{}key\"'.format(name, delimiter))
    

def color_generator():
    initial = np.array([[1.0,0,0],
                        [0.0,1.0,0.0],
                        [0.0,0.0,1.0]],
                        dtype=np.float)
    i = 0
    while True:
        if i < len(initial):
            color = initial[i]
        else:
            color = np.random.random(3)
        i += 1

        color = str(color).strip()[1:-1].strip()
        print(color)
        yield color


        
def calculate_edge_attributes(graph):
    '''
    Our logical groups are derived from the 'parent groups' node attribute.
    This is a convient place without a lot of duplication, but we would also
    often like to know which edges are optional, and which edges can be 
    substituted for other edges. 

    This function calculates properties for edges based on the 'parent groups'
    data stored per- node.

    Parameters
    -----------
    graph: TechGraph object
    '''
    
    edges = collections.deque()
    colors = color_generator()
    for parent, children in graph.edge.items():
        for child, child_attr in children.items():
            if 'parent groups' not in graph.node[child]:
                continue
            for group_number, group in enumerate(graph.node[child]['parent groups']):
                if not is_sequence(group):
                    continue
                optional = None in group
                
                group_id = '|'.join([child, str(group_number)])
                color = next(colors)
                for i in group:
                    if i is None: continue
                    current_parent, key = split_key(i)
                    if optional:
                        attributes = {'style' : 'dotted'}
                    else:
                        attributes = {'substitutes' : group,
                                      'color' : color}
                    attributes['optional'] = optional
                    attributes['group_id'] =  group_id
                    edge = {'u' : current_parent,
                            'v' : child,
                            'key' : key,
                            'attr_dict' : attributes}
                    edges.append(edge)
    # we do this at the end so all modifications are done after traversal
    # if the edge exists, it will modify the attributes nicely
    for e in edges:
        graph.add_edge(**e)
        
        
if __name__ == '__main__':
    
    '''
    A techgraph needs to be able to 
    Question: if you can't represent a pancake recipe in graph form
    how the f is a spaceship going to work? We need to be able to 
    indicate logical groupings of edges.
    
    Specifically, this recipe: 
    http://www.marthastewart.com/338185/basic-pancakes
    '''
        
    # the node we're going to be defining parents for
    child = 'basic pancakes'


    # list dict to pass to graph.add_edge 
    parents = [{'u' : 'all-purpose flour',         'attr_dict' : {'quantity' : '1.0 cups/batch'}},
               {'u' : 'granular white sugar',      'attr_dict' : {'quantity' : '2.0 tablespoons/batch'}},
               {'u' : 'baking powder',             'attr_dict' : {'quantity' : '2.0 teaspoons/batch'}},
               {'u' : 'table salt',                'attr_dict' : {'quantity' : '0.5 teaspoons/batch'}},
               {'u' : 'milk',                      'attr_dict' : {'quantity' : '1.0 cups/batch'}},
               {'u' : 'unsalted butter',           'attr_dict' : {'quantity' : '2.0 tablespoons/batch'}},
               {'u' : 'chicken egg',               'attr_dict' : {'quantity' : '1.0 egg/batch'}},
               {'u' : 'vegetable oil', 'key' : 0,  'attr_dict' : {'quantity' : '2.0 tablespoon / batch'}},
               {'u' : 'vegetable oil', 'key' : 1,  'attr_dict' : {'quantity' : '1.0 tablespoon / batch'}}]

    # we need to be able to encode that you can substitute vegetable oil for butter
    # also the optional maple syrup needs to be conveyed
    # this is a proposal for switching between edges
    # - if a parent name is included as a top-level element it is a required edge
    # -- if a parent name is *NOT* included, it is implied to be required
    # - if multiple nodes are in a tuple like ('stuff', 'things', 'eggs') it means
    #   that any one of those will satisfy the requirement
    parent_groups = ['all-purpose flour',     # not in a tuple, so a required edge
                     'granular white sugar',  # not in a tuple, so a required edge
                     'baking powder',         # same...
                     'table salt',
                     'milk',
                     ('unsalted butter', 'vegetable oil'), # a substitution tuple, 
                                                           # we can use unsalted butter, OR vegetable oil
                     'chicken egg',
                     'vegetable oil',
                     (None, 'Maple Syrup')] # a substitution tuple with None, or optional component


    # since all the required edges are implied,
    # we can just do the ones with ANY tuples
    parent_groups = [('unsalted butter', 'vegetable oil:1'), # a substitution tuple
                     (None, 'Maple Syrup')]                  # maple syrup is optional                


    # the graph should allow multiple edges
    g = TechGraph()
    for parent in parents:
        g.add_edge(v=child, **parent)
        
    g.node[child]['parent groups'] = parent_groups
    g.add_edge('basic pancakes', 'pancakes', attr_dict={'quantity': '1 batch/batch'})
    g.format_nodes()
    g.calculate_edge_attributes()

    with open('tech.svg', 'wb') as f:
        f.write(g.to_svg())
