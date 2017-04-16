# techgraph


### Introduction
TechGraph is a project to capture the progression of real technologies with a directed graph. 

The idea is that whether you wanted to make a waffle iron or space station you could list what you were starting with (such as 'Pre-industrial', 'Fire', etc.) and then find the shortest path of things required to actually produce the object using information in the nodes and edges.

Some good starting points for research are the [timeline of historic inventions on Wikipedia](https://en.wikipedia.org/wiki/Timeline_of_historic_inventions) or the [Youtube channel of How It's Made](https://www.youtube.com/channel/UCELt4nocnWDEnYJmov4zqyA)


### Graph Structure
There are a lot of ways to structure a graph representing technology. The common one found in games is a [tech tree](https://en.wikipedia.org/wiki/Technology_tree). Our TechGraphs are directed graphs, but enforce no particular structure. The obvious thing to enforce would be a [forest](https://en.wikipedia.org/wiki/Tree_(graph_theory)), but we're going to leave the structure as flexible as possible unless a compelling argument is made.   

##### nodes: represent things
Nodes in the TechGraph generally refer to an object, process, or state. Examples include:

* Rope
* Bessemer Process
* Knee Mill
* Copper
* Aluminium Alloy 6061 T6
* USA 1901 

Each node has key- value data associated with it, called 'attributes'. A node may have any attribute, but it also *must* have the attribute **all_parents** explictly defined as either **True** or **False**. This is a way to encode in graph form the idea that there usually there are multiple ways to skin a cat. The all_parents attribute is slightly confusing, but the alternatives are even more confusing. Other attributes which are optional, but could be useful include: 
* description
  * a brief description of what this node is
* procedure
  * how does one combine the parent nodes to produce this node?
* units
  * what is the unit this node is measured in?
          
##### edges: represent the things required to make other things
An edge is a connection between a parent node and a child node, implying that in order to produce the child, the parent is required. An edge has no mandatory attributes, and can have any key-value data defined. Some examples of attributes which could be useful are:  
* quantity
  * how many units of the parent are required to make one unit of the child?
* person-hours
  * what is the approximate number of person-hours required to make 1 canonical unit of the child (person-hours / unit)
           
### Example

![Pancakes](https://raw.github.com/mikedh/techgraph/master/docs/pancake.png)
These two competing pancake recipes of questionable edibility show required edges in purple and optional edges in black. Note that whether an edge is mandatory was inferred from the all_parents flag set on the *child node of the edge*.

```
'Hemp fiber'          REQUIRED->
'Twisting Apparatus   REQUIRED->  (ALL PARENTS) 'Hemp Rope'    OPTIONAL\
                                                                         -> (ANY PARENT)'Rope'
'Nylon fiber'         REQUIRED->  (ALL PARENTS) 'Nylon Rope'   OPTIONAL/
'Twisting Apparatus'  REQUIRED-> 
```

    
If there is a more generic form of an object, the generic form
should be the child of the specific form:
```
'Bridgeport Series 1 Knee Mill' -> (ANY PARENT) 'Manual Milling Machine'
'Aluminium Alloy 6061-T6'       -> (ANY PARENT) 'Aluminium Alloy'
```  
## Content Guidelines

* Should all be BSD or BSD compatible. 
* 3D models should be STEP AP214 or PLY
* Mechanical drawings and other schematics should be in vector formats, PDF or DXF