from stat_parser import Parser
parser = Parser()

tree_obj = parser.parse("This is a very nice sentence")

# tree_obj is of type nltk.tree.Tree
# http://www.nltk.org/_modules/nltk/tree.html