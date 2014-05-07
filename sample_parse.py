from stat_parser import Parser
from graph_generator import GraphGenerator, get_leaves
from nltk.tree import ParentedTree

parser = Parser()

tree_obj = parser.parse("The food was on the table where the child likes to eat")
ptree = ParentedTree.convert(tree_obj)
gg = GraphGenerator()
gg.update_graph(ptree)
gg.draw_graph("graph")
# tree_obj is of type nltk.tree.Tree
# http://www.nltk.org/_modules/nltk/tree.html