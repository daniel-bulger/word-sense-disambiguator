import multiprocessing
import threading
import nltk
from nltk.tree import ParentedTree
from stat_parser import Parser
from graph_generator import GraphGenerator

print "Loading corpus"
data = open("data/extracted.txt").read()
print "Tokenizing sentences"
sentences = nltk.tokenize.sent_tokenize(data)
sentences = sentences[:10]

thread_count = multiprocessing.cpu_count()
sentence_tasks = [sentences[i::thread_count] for i in xrange(thread_count)]

print "Using %d threads" % (len(sentence_tasks),)

print "Creating graph"
gg = GraphGenerator()

def delegate(task):
    global gg
    print "Creating parser"
    parser = Parser()
    for i, sentence in enumerate(task):
        print "Parsing sentence %d" % (i,)
        parsed = parser.parse(sentence)
        print "Adding sentence %d to graph" % (i,)
        gg.update_graph(ParentedTree.convert(parsed))

for i, task in enumerate(sentence_tasks):
    print "Delegating task %d" % (i,)
    t = threading.Thread(target=delegate, args=(task,))
    t.start()

for task in sentence_tasks:
    t.join()

gg.draw_graph("output.png")