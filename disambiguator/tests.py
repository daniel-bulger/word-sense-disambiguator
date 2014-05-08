from stat_parser import Parser
from graph import Graph,get_leaves,merge_graphs
from nltk.tree import ParentedTree

parser = Parser()
trees = []
trees.append(parser.parse("The food was on the table where the child likes to eat"))
trees.append(parser.parse("The money is on the table"))
trees.append(parser.parse("Put the data in the table"))
trees.append(parser.parse("Add more rows to the database table"))
trees.append(parser.parse("Add more rows to the database table"))
trees.append(parser.parse("Why is the table empty It should have data in it"))
trees.append(parser.parse("Do not put your elbows on the table while you eat"))

for tree in trees:
	tree = ParentedTree.convert(tree)
graphs = []
for tree in trees:
	g = Graph()
	g.update(tree)
	graphs.append(g)
new_graph = merge_graphs(graphs)
new_graph.draw("new_graph")
new_graph.save_to_file("new_graph.gml")
new_graph.load_from_file("new_graph.gml")
print new_graph.get_median_relatedness()
print new_graph.get_senses("table")