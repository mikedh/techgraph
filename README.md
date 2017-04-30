# techgraph


### Introduction
TechGraph is a project to describe all of technology with a directed graph. The grand vision is to someday include nodes for everything humans are able to build and do. 

The idea is that if you wanted to make something (waffle iron, space station, etc) you could list what you were starting with (for example, 'Fire', 'USD', 'Steel' etc.) and then find the shortest path of things required to produce the object using information in the nodes and edges.

Some good starting points for research are the [timeline of historic inventions on Wikipedia](https://en.wikipedia.org/wiki/Timeline_of_historic_inventions) or the [Youtube channel of How It's Made](https://www.youtube.com/channel/UCELt4nocnWDEnYJmov4zqyA)


### Graph Structure
There are a lot of ways to structure a graph representing technology. The common one found in games is a [tech tree](https://en.wikipedia.org/wiki/Technology_tree). Our TechGraphs are directed graphs (inherits from networkx.MultiDiGraph), but enforce no particular structure. The obvious thing to enforce would be a [forest](https://en.wikipedia.org/wiki/Tree_(graph_theory)), but we choose not to until it is demonstrated to be better.

#### nodes: represent things
Nodes in the TechGraph generally refer to an object, process, or state. Examples include things like 'Rope', 'Bessemer Process', 'Pancakes', 'Knee Mill', 'Copper'.

Each node has key- value data associated with it, called 'attributes'. The most important of these is `parent_groups`, which is how logic for optional components and substitutions are defined. For example, in a pancake recipe which allows substituting vegetable oil for butter, and has optional maple syrup:

```
# the node we are starting with
child = 'basic pancakes'

# we only need to specify the parents of the child whose edges
# require substitution logic
parent_groups = [('unsalted butter', 'vegetable oil'), # we can use unsalted butter, OR vegetable oil
			     (None, 'Maple Syrup')]                # maple syrup is optional     
```


Examples of things you might want to set for a node: 
* `parent groups`
  * define the logic for substitutions
* `description`
  * a brief description of what this node is
* `procedure`
  * how does one combine the parent nodes to produce this node?
* `units`
  * what is the unit this node is measured in?

#### edges: represent the prerequisites to make things
An edge is a connection between a parent node and a child node, implying that in order to produce the child, the parent is required. An edge has no mandatory attributes, and can have any key-value data defined. Some examples of attributes which could be useful are:  
* quantity
  * how many units of the parent are required to make one unit of the child?
* person-hours
  * what is the approximate number of person-hours required to make 1 canonical unit of the child (person-hours / unit)
           
### Example

```
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
g = nx.MultiDiGraph()
g = TechGraph()
for parent in parents:
	g.add_edge(v=child, **parent)
```

![Pancakes](https://raw.github.com/mikedh/techgraph/master/docs/pancakes.png)

The maple syrup is optional, and the two edges of the same color represent an OR, so either edge will satisfy the need.



## Content Guidelines

* Should all be BSD or BSD compatible. 
* 3D models should be STEP AP214 or PLY
* Mechanical drawings and other schematics should be in vector formats, PDF or DXF