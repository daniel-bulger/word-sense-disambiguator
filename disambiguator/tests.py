from stat_parser import Parser
from graph import Graph,get_leaves,merge_graphs
from nltk.tree import ParentedTree

parser = Parser()
trees = []
trees.append(parser.parse("The food was on the table where the child likes to eat"))
trees.append(parser.parse("The money is on the table"))
trees.append(parser.parse("Put the data in the table"))
for tree in trees:
	tree = ParentedTree.convert(tree)
graphs = []
for tree in trees:
	g = Graph()
	g.update(tree)
	graphs.append(g)
new_graph = merge_graphs(graphs)
new_graph.draw("new_graph")