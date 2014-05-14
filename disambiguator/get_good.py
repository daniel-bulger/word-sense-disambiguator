from nltk.corpus import brown
import sys
from graph import Graph,merge_graphs
from nltk.tree import Tree, ParentedTree
from stat_parser import Parser
import cPickle as pickle
import xml.etree.ElementTree as ET

print "Welcome"
query = sys.argv[1]

def depth_parse(cons):
    if cons.find('tok') is not None:
        token = cons.find('tok')
        return ParentedTree(token.get('cat'), [token.get('base')])
    else:
        children = []
        if len(cons.findall('cons')) == 0:
            raise Exception("Failed to parse")

        for child in cons.findall('cons'):
            children.append(depth_parse(child))
        return ParentedTree(cons.get('cat'), children)

try:
    trees = pickle.load(open("trees_cache"))
    print "Loaded from cache"
except:
    print "Loading from file"
    data = ET.parse('parsed.xml')
    root = data.getroot()

    trees = []

    for sentence in root.findall('sentence'):
        try:
            parsed = depth_parse(sentence)
        except Exception:
            continue

        trees.append(parsed)

    pickle.dump(trees, open("trees_cache", "w"), pickle.HIGHEST_PROTOCOL)

relevant_trees = []

for tree in trees:
    if query in tree.leaves():
        relevant_trees.append(tree)

for tree in relevant_trees:
    tree = ParentedTree.convert(tree)
graphs = []
for tree in relevant_trees:
    g = Graph(query)
    g.update(tree)
    graphs.append(g)
print "Merging graphs" 
new_graph = merge_graphs(graphs)
# print "Drawing graph (fake)"
# new_graph.draw("new_graph_"+query)
print "Getting senses"
print new_graph.get_senses_markov()