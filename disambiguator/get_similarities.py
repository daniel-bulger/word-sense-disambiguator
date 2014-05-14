from nltk.corpus import brown
import sys
from graph import Graph,merge_graphs
from nltk.tree import ParentedTree
from stat_parser import Parser
parser = Parser()

user_sentence = sys.argv[1]
query = sys.argv[2]
trees = []
done = 0
# for sentence in brown.sents():
# 	if done >= 20:
# 		break
# 	if not query in sentence:
# 		continue
# 	if len(sentence) > 20:
# 		continue
# 	try:
# 		trees.append(parser.parse(" ".join(sentence)))
# 		done += 1
# 		print done
# 	except:
# 		print "oops couldn't parse that one"
# trees = []
# trees.append(parser.parse("The food was on the table where the child likes to eat"))
# trees.append(parser.parse("I eat food at the table"))
# trees.append(parser.parse("I eat the food that is on the table"))
# trees.append(parser.parse("The money is on the table"))
# trees.append(parser.parse("Put the data in the table"))
# trees.append(parser.parse("Add more rows to the database table"))
# trees.append(parser.parse("Why is the database table empty It should have data in it"))
# trees.append(parser.parse("Do not put your elbows on the table while you eat"))
# trees.append(parser.parse("I like to eat at the kitchen table"))
# trees.append(parser.parse("I like to eat food at the kitchen table"))

trees = []
trees.append(parser.parse("a database table stores rows"))
trees.append(parser.parse("kitchen table"))
trees.append(parser.parse("food on kitchen table"))
trees.append(parser.parse("put rows in database table"))
trees.append(parser.parse("damaged wooden kitchen table"))
trees.append(parser.parse("wooden table"))
trees.append(parser.parse("the table that had been forgotten for years became damaged"))
trees.append(parser.parse("the database table for our favorite client, Bob's bakery, needs more rows"))
trees.append(parser.parse("the database table that stores sensitive client data should be secure"))
trees.append(parser.parse("the database table that stores passwords should be secure"))
trees.append(parser.parse("Motion to table discussion until later"))
trees.append(parser.parse("Please table the motion until a later date"))
trees.append(parser.parse("We should table, if not reject, this motion"))


for tree in trees:
	tree = ParentedTree.convert(tree)
graphs = []
for tree in trees:
	g = Graph(query)
	g.update(tree)
	graphs.append(g)
print "Merging graphs"
new_graph = merge_graphs(graphs)
print "Drawing graph (fake)"
new_graph.draw("new_graph_"+query)
print "Getting senses"
print new_graph.get_senses()
print "Prediction is..."
print new_graph.get_predicted_sense(ParentedTree.convert(parser.parse(user_sentence)))
#new_graph.print_relatedness_to_target_in_order()